from netmiko import (ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException)
from tkinter import messagebox
import itertools
import builtins
import re
from lg import *
from ip_nestedDict import remoteSites #dictionary
platform = 'cisco_ios'
ls_hosts=[] # nested lists of RTR/SWs per site, built from remoteSites dictionary
ls_rtr=[]   # list of routers built from ls_hosts
ls_sw=[]    # list of switches built from ls_hosts

for key in remoteSites.keys(): # K:V (nested lists) of dictionary- 'SiteName3':[['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']],
    hosts = remoteSites[key]
    ls_hosts.append(hosts)
for list0, devices in enumerate(ls_hosts):   # enum lists of sites-            [['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']],
    for list1, device in enumerate(devices): # enum lists of devices per site-  ['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']
        if list1!=0: # list index is not 0 in list of lists                                 ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']
            for list2, sw in enumerate(device): # enum by switch in list of switches
                ls_sw.append(sw) # append switch ips to list ls_sw
        else:
            for list2, rtr in enumerate(device): # enum lists of routers, index 0 per site
                ls_rtr.append(rtr) # append rtr ips to list ls_rtr
# iterates switch IPs as host from the router list
for sw_host in ls_sw:
    try:
        ch = ConnectHandler(ip = sw_host, device_type = platform)
        print('logged into host: ', sw_host)
        span_c = ch.send_command('sh span vlan xx')   # span_c returns sh span vlan xx (management vlan id scrubbed)
        int_c = ch.send_command('sh int status')   # int_c returns sh int status
        print(span_c, int_c)
        
        # int_regex finds all interfaces from sh int status
        int_regex = re.findall(r'(\w{2}\d/(?:\d{1,2}/)?\d{1,2}\b)', int_c) #[2]
        # po_regex finds all Port Channels from sh int status
        po_regex = re.findall(r'(Po\d{1,2}\b)', int_c)
        # span_regex finds all Root interfaces from sh span vlan xx
        span_regex = re.findall(r'(\w{2}\d/(?:\d{1,2}/)?\d{1,2}\b)(?:.*?)Root [^ID]', span_c) #[1]
        if po_regex: # if a Port Channel is found - 
            print('----------')
            for x in po_regex:
                print('I found Port Channel :{x}'.format(x = x)) # Prints the Port Channel number from the po_regex list
        print('----------')
        print('Ints   |   Root')
        for x, y in itertools.zip_longest(int_regex, span_regex): 
            print(x,' | ', y) # Prints all Ints and Root Ints side-by-side for comparison

        # quick tkinter messagebox forcing pause & giving user chance to QC results
        intDifspan_ck = messagebox.askyesno("Question","Everything look good?")
        if intDifspan_ck == True:
            if po_regex: # if a Port Channel was found -
                for x in po_regex:
                    po_tmp = 'sh int {}'
                    po_f = po_tmp.format(x)
                    po_c = ch.send_command(po_f) # sends sh int PO

                    # po_int_ls finds all interfaces within the Port Channel
                    po_int_ls = re.findall(r'([A-Za-z]{2}\d/(?:\d{1,2}/)?\d{1,2}\b)(?:.*?)', po_c)

                    # list comparision of all ints from sh int status (int_regex) and root ints from sh span vlan 255 (span_regex)
                    sp_re = set(span_regex) #[1]
                    dif = [x for x in int_regex if x not in sp_reg] #[3]=[2].dif[1]               

                    # list comparison of dif and interfaces found in sh int PO (po_int_ls). -
                        # returns interfaces to apply Root Guard on.
                    sp_reg2 = set(po_int_ls) #[4]
                    dif2 = [x for x in dif if x not in sp_reg2] #[5]=[3].dif[4]
                    print('----------')
                    print('Ints   |   Root')
                    for x, y in itertools.zip_longest(dif2, po_int_ls):
                        print(x,' | ', y)
                        
                    # another message box prompting user to review the interfaces before configuration
                    intDifpo_ck = messagebox.askyesno("Question","Everything look good?")
                    if intDifpo_ck == True:                
                        for x in dif2:
                            int_tmp = 'interface {}'
                            intPo_c = int_tmp.format(x)
                            send_int = ch.send_config_set(intPo_c, exit_config_mode=False)
                            print(send_int)
                            send_span = ch.send_config_set('spanning-tree guard root', exit_config_mode=False)
                            print(send_span)
                    else:
                        print('skipping device')

            else: # no Port Channel was found
                sp_reg = set(span_regex)
                dif = [x for x in int_regex if x not in sp_reg] #returns non-root ints
                print(dif)
                for x in dif:
                    int_tmp = 'interface {}'
                    intGi_c = int_tmp.format(x) 
                    send_int = ch.send_config_set(intGi_c, exit_config_mode=False)
                    print(intGi_c)
                    send_span = ch.send_command('spanning-tree guard root', exit_config_mode=False)
                    print(spanT_c)
        else:
            print('skipping device')
    except(NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        print('{}: {}'.format(host, error))
