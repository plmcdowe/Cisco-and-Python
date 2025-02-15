from netmiko import (ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException)
from tkinter import messagebox
import itertools
import builtins
import time
import re
from lg import *
from ip_nestedDict import remoteSites
platform = 'cisco_ios'

ls_sw=[]
ls_rtr=[]
ls_hosts=[]
for key in remoteSites.keys():  #pulls out nested lists from dictionary
    hosts = remoteSites[key]
    ls_hosts.append(hosts)   
for list0, devices in enumerate(ls_hosts):   #enum list of sites  
    for list1, device in enumerate(devices): #enum list of devices per site
        if list1!=0:            
            for list2, sw in enumerate(device):
                ls_sw.append(sw) #based on positional enumeration, builds a list of all switches
        else:
            for list2, rtr in enumerate(device):
                ls_rtr.append(rtr) #based on positional enumeration, builds a list of all routers
                
for host in ls_rtr:
    try:
        ch = ConnectHandler(ip = host, device_type = platform)
        print('logged into host: ',host)
        enable=ch.find_prompt()

        denial='fxols_power_denial_detected'
        offhook='fxols_offhook_release'

        good_ls=[]
        bad_ls=[]

        ## This block was for updating MGCP binding on VoIP subinterface prior to SIP trunk reconfig. ##
        #used for pulling in the Gi0/0/0 or 0/0/1 
        shIPbr=ch.send_command('sh ip int br | i \.XX')#VoIP subinterface removed
        r_voipIP=re.findall(r'(?:Gi?)(\d{1}\/\d{1}\/\d{1}\.XX)', shIPbr, re.S)
        print(r_voipIP)
        shIPdomain=ch.send_command('sh run | i ip domain')
        print(shIPdomain)
        shMGCPbind=ch.send_command('sh run | i mgcp bind')
        r_MGCPcontrol=re.findall(r'(?:control.*?)(\d{1}\/\d{1}\/\d{1}\.\d{1,2})', shMGCPbind, re.M)
        r_MGCPmedia=re.findall(r'(?:media.*?)(\d{1}\/\d{1}\/\d{1}\.\d{1,2})', shMGCPbind, re.M)
        print(r_MGCPcontrol)
        print(r_MGCPmedia)
        for IP, cntrl in itertools.zip_longest(r_voipIP, r_MGCPcontrol):
            if IP not in cntrl:
                control=[f'mgcp bind control source-interface GigabitEthernet{IP}']
                s_control=ch.send_config_set(control, cmd_verify=False, delay_factor=3)
                print(s_control)                
        for IP, media in itertools.zip_longest(r_voipIP, r_MGCPmedia):
            if IP not in media:
                media=ch.send_config_set[f'mgcp bind media source-interface GigabitEthernet{IP}']
                s_media=ch.send_config_set(media, cmd_verify=False, delay_factor=3)
                print(s_media)
        ## End Block for MGCP binding ##

        #pulls in the fxo interfaces and their up/down status, then appends to a down list or an up list 
        shVoicePort=ch.send_command('sh voice port sum | i fxo-')
        r_voicePort=re.findall(r'(\d\/\d\/\d)(?:.*?)(fxo-ls)(?:.*?)(\w{2,4})(?:.*?)(do.*?[e|k])(?:.*?)([i|o].*?[e|k])', shVoicePort, re.M)
        print(r_voicePort)
        down_ls=[]
        up_ls=[]        
        for i in r_voicePort:
            if 'down' in i[2]:
                down_ls.append(i[0])
            else:
                up_ls.append(i[0])               
        print('down FXO: ',down_ls)
        print('up FXO: ',up_ls)

        #pulls in all of the dial-peer configs
        shDialPeer_Port=ch.send_command('sh run | i dial-peer|destination-pattern|^_port_(.*)/(.*)/(.*)')

        #clears out all the fxo interface dial-peer config
        r_dialPeer=re.findall(r'(?:voice\s?)(\d+?)(?:\spots)', shDialPeer_Port, re.S)
        for i in r_dialPeer:
            no_dialPeer=[f'no dial-peer voice {i} pots']
            s_noDial=ch.send_config_set(no_dialPeer, cmd_verify=False, delay_factor=3)
            #print(s_noDial)
            time.sleep(1)

        #for any shutdown fxo port, no shut it
        if down_ls:
            for i in down_ls:
                noShut=[f'voice-port {i}', 'no shut']
                s_noShut=ch.send_config_set(noShut, cmd_verify=False, delay_factor=3)
                up_ls.append(i)
                time.sleep(1)

        dialPeerINT=[]
        for Int in up_ls:
            split_ls=[]
            for i in Int.split('/'):
                split_ls.append(i)
            split_ls=''.join(split_ls)
            dialPeerINT.append(split_ls)
        print(dialPeerINT)

        #starts the voice port module debug
        debugVPM=ch.send_command('debug vpm all')
        print(debugVPM)

        #applies the MGCP service and the toll-free dial peer to each fxo interface        
        for r, i in itertools.zip_longest(dialPeerINT, up_ls):
            rule_MGCP=[f'dial-peer voice 999{r} pots', 'service mgcpapp', f'port {i}']                        
            s_MGCP=ch.send_config_set(rule_MGCP, cmd_verify=False, exit_config_mode=False, delay_factor=3)            

            rule_31=[f'dial-peer voice 3111{r} pots', 'destination-pattern 31[2-9]..[2-9]......', f'port {i}', 'forward-digits 11']
            s_31=ch.send_config_set(rule_31, cmd_verify=False, delay_factor=3)

            time.sleep(5)

        #clears the logg            
            ch.write_channel('clear logg\n')
            time.sleep(2)
            ch.write_channel('y\n')
            time.sleep(10)

        #notice to admin to place a toll-free call from their deskphone which is in the remote-site's calling search space - generating vpm loggs
            print('call now')

            time.sleep(20)

        #regex for 'power_denial_detected' and the offhook status
            loggDenial=ch.send_command(f'sh logg | i {denial}|{offhook}')
            
            time.sleep(2)
            
            r_denial=re.findall(r'(?:nt:\s\[?)(\d\/\d\/\d)(?:,.*\]fxols_p.*?)', loggDenial, re.M)
            r_hook=re.findall(r'(?:nt:\s\[?)(\d\/\d\/\d)(?:,.*\]fxols_o.*?)', loggDenial, re.M)
            print(loggDenial)
            print(r_denial)
            print(r_hook)

        #if the fxo interface went off-hook, it is added to the "good list"            
            if r_denial==r_hook:
                good_ls.append(r_hook[0])
            else:
                for i in r_denial:
                    bad_ls.append(i)
                for i in r_hook:
                    good_ls.append(i)
            
            print('good: ',good_ls)
            print('bad: ',bad_ls)

            time.sleep(2)        

        #the testing dial-pears are removed
            noRule_MGCP=[f'no dial-peer voice 999{r} pots']                        
            s_noMGCP=ch.send_config_set(noRule_MGCP, cmd_verify=False, exit_config_mode=False, delay_factor=3)
            #print(s_noMGCP)

            noRule_31=[f'no dial-peer voice 3111{r} pots']
            s_no31=ch.send_config_set(noRule_31, cmd_verify=False, delay_factor=3)
            #print(s_no31)
            
            time.sleep(2)

        #the bad interfaces are shut and a description is added
        for i in bad_ls:
            shut=[f'voice-port {i}', 'shut', 'description power_denial']
            s_shut=ch.send_config_set(shut, cmd_verify=False, delay_factor=3)
            #print(s_shut)
            time.sleep(2)

        dialPeerGood=[]
        inwardDPGood=[]
        for Int in good_ls:
            split_ls=[]
            dp_ls=[]
            for i in Int.split('/'):
                split_ls.append(i)
                dp_ls.append(i)
            for i in split_ls:
                if '0' in i[0]:
                    reorder=[2, 0, 1]
                    split_ls=[split_ls[i] for i in reorder]
            dp_ls=''.join(dp_ls)
            dialPeerGood.append(dp_ls)
            split_ls=''.join(split_ls)
            inwardDPGood.append(split_ls)
        print(dialPeerGood)
        print(inwardDPGood)

    #Dial peers are applied to good fxo interfaces.
        time.sleep(2)
        if good_ls!='None':
            for r, i in itertools.zip_longest(dialPeerGood, good_ls):
                rule_MGCP=[f'dial-peer voice 999{r} pots', 'service mgcpapp', f'port {i}']                        
                s_MGCP=ch.send_config_set(rule_MGCP, cmd_verify=False, exit_config_mode=False, delay_factor=3)
                #print(s_MGCP)
                
            for r, i in itertools.zip_longest(inwardDPGood, good_ls):                
                rule_InwardDial=[f'dial-peer voice {r} pots', 'incoming called-number .', 'direct-inward-dial', f'port {i}']            
                s_InwardDial=ch.send_config_set(rule_InwardDial, cmd_verify=False, exit_config_mode=False, delay_factor=3)
                #print(s_InwardDial)
                
            for r, i in itertools.zip_longest(dialPeerGood, good_ls):
                rule_911=[f'dial-peer voice 911{r} pots', 'destination-pattern 911', f'port {i}', 'forward-digits 3']            
                s_911=ch.send_config_set(rule_911, cmd_verify=False, exit_config_mode=False, delay_factor=3)
                #print(s_911)
                
            for r, i in itertools.zip_longest(dialPeerGood, good_ls):
                rule_9911=[f'dial-peer voice 9911{r} pots', 'destination-pattern 9911', f'port {i}', 'forward-digits 3']
                s_9911=ch.send_config_set(rule_9911, cmd_verify=False, exit_config_mode=False, delay_factor=3)
                #print(s_9911)
                
            for r, i in itertools.zip_longest(dialPeerGood, good_ls):
                rule_31=[f'dial-peer voice 3111{r} pots', 'destination-pattern 31[2-9]..[2-9]......', f'port {i}', 'forward-digits 11']
                s_31=ch.send_config_set(rule_31, cmd_verify=False, delay_factor=3)
                #print(s_31)      

    #The final config is printed out for the Admin to review.
        shVoicePort=ch.send_command('sh voice port sum | i fxo-')
        r_voicePort=re.findall(r'(\d\/\d\/\d)(?:.*?)(fxo-ls)(?:.*?)(\w{2,4})(?:.*?)(do.*?[e|k])(?:.*?)([i|o].*?[e|k])', shVoicePort, re.M)
        for i in r_voicePort:
            print(i)
        ch.send_command('no debug all')
        ch.disconnect                
    except(NetmikoTimeoutException, NetmikoAuthenticationException) as error: 
        print('{}: {}'.format(host, error))

