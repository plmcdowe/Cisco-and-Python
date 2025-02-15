from netmiko import (ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException)
from tkinter import messagebox
import itertools
import builtins
import re
from lg import *
from regexFunctions import *
from ip_nestedDict import remoteSites
platform = 'cisco_ios'
ls_sw=[]
ls_rtr=[]
ls_hosts=[] #nested lists of RTR/SWs per site, built from remoteSites dictionary

for key in remoteSites.keys():  #pulls out nested lists from dictionary
    hosts = remoteSites[key]
    ls_hosts.append(hosts)   
for list0, devices in enumerate(ls_hosts):   #enum list of sites  
    for list1, device in enumerate(devices): #enum list of devices per site
        if list1!=0:            
            for list2, sw in enumerate(device): #enum lists of switches
                ls_sw.append(sw) #appends switch ips to list ls_sw
        else:
            for list2, rtr in enumerate(device): #enum lists of routers
                ls_rtr.append(rtr) #appends router ips to list ls_rtr
for host in ls_rtr: #iterates string item (RTR IPs) as host for logging in
    start_re = messagebox.askyesno("Question","Next device?")
    if start_re == True:
        try:
            ch = ConnectHandler(ip = host, device_type = platform)
            print('logged into host: ',host)
            enable = ch.find_prompt() #waits till '#'
            print('')
            
            ipIntCommand = ch.send_command('sh ip int br | e unassigned') #sends sh ip int br exluding 'unassigned' interfaces
            print('----------sh ip int br----------')
            print(ipIntCommand)
            print('')

            regex_ipInt = re.findall(r'(Gi\d{1}/\d{1}/\d{1}.\d{1,3})(?:.*?)(u|\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', ipIntCommand, re.S) #creates list of interface and ip groups -treats like nested lists
            print("----------regex finds [('SubInt', 'IP'), ...]----------")
            print(regex_ipInt)
            print('')

            Interfaces = [i for sublist in regex_ipInt for i in sublist if '/' in i] #creates list of interfaces from regex_ipInt
            IPs = [i for sublist in regex_ipInt for i in sublist if '/' not in i]   #creates list of IPs from regex_ipInt
            #print(IPs)
            #print(Interfaces)
            #print('')
        
            for i, n in itertools.zip_longest(IPs, Interfaces): #formated print of IP and interface
                print('IP: '+i+' | '+'INT: '+n)
            
            list_accessGroupInts = []
            list_subNets = []    
            for i, n in itertools.zip_longest(IPs, Interfaces): #uses IP from sh int br
                shRunInt = 'sh run int {} | i ^int.*Gi.*net(.*)/(.*)/(.*)\.[0-9]|^_ip_ad.*s_[0-9].*\.[0-9]$|^_ip_access-group_[DA]' #format where {} is iterated variable from interfaces
                f_shRunInt = shRunInt.format(n) #formats the above string, {n} from list interfaces
                shRunInt_c = ch.send_command(f_shRunInt) #netmiko sends the formated string as command
                print(shRunInt_c)
                IPsearchRegex = re.findall(r'(?:GigabitEthernet\d{1}/\d{1}/\d{1}.\d{1,3}.*?)(?:ip address '+i+'?) (\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', shRunInt_c, re.S) 
                print(IPsearchRegex)    #IPsearchRegex iterates PRIMARY IP as i in regex to find only the PRIMARY IP's mask
                print('')
                print('--------------------')
                accessGroup = accessGroupRegex(shRunInt_c)  #creates list of access-group
                list_accessGroupInts.append(accessGroup)    #appends the regex list-result to access group list
                list_subNets.append(IPsearchRegex)
            print(list_accessGroupInts)
            print(list_subNets)
            print('--------------------')

            noACL_IP=[]
            noACL_ints=[]
            noACL_masks=[]
            for (Int, IP, nets, acl) in itertools.zip_longest(Interfaces, IPs, list_subNets, list_accessGroupInts):
                if len(acl)==0: #if the lenght of item (acl) in list (accessGroupInts) is empty,
                    noACL_IP.append(IP)
                    noACL_ints.append(Int)  #append the IP 
                    noACL_masks.append(nets)    #and subnet mask from corresponding indecies to the noACL lists

            print(noACL_ints)
            print(noACL_masks)
            print('--------------------')

            strMasks = [mask for sublist in noACL_masks for mask in sublist] #list comp to pull the subnetmasks from list of interfaces with no ACL
            wildCardLast=[]
            inverseMask = []
            for m in strMasks: #for each mask  
                wildcard=[]
                for n in m.split('.'): #for each octet of mask when split on decimals
                    net = 255 - int(n) #subtract octet from 255
                    wildcard.append(str(net)) #appends each inversed octet to the wildcard list
                wildcard = '.'.join(wildcard) #joins each with decimal
                inverseMask.append(wildcard) #appends the reasabled inverse mask to inverseMask list
            
            vlans = [v.split('.') for v in noACL_ints] #splits the vlan on decimal
            vlan = [v for sublist in vlans for v in sublist if '/' not in v] #list comp 
            
            finalIP=[]
            finalInt=[]
            finalInverseMask=[]
            finalVlan=[]
            for (ips, ints, mask, vlans) in itertools.zip_longest(noACL_IP, noACL_ints, inverseMask, vlan): #
                if vlans != '99': #if the vlan is not 99
                    finalIP.append(ips)
                    finalInt.append(ints)
                    finalInverseMask.append(mask)
                    finalVlan.append(vlans)
                
            print('--------------------')    
            print('PRIMARY IPs: ',finalIP)
            print('INTERFACES: ',finalInt)
            print('WILDCARD: ',finalInverseMask)
            print('VLAN: ',finalVlan)
            print('')
            print('----------Review the commands:----------')  
            print('conf t')
## This whole section is formatting the acl and printing for review before sending the actual commands through netmiko            
            for (ip, mask, vlan) in itertools.zip_longest(finalIP, finalInverseMask, finalVlan):
                print('')        
                acl_name_c = 'ip access-list extended DATA-VLAN_{}'
                f_acl_c = acl_name_c.format(vlan)
                print(f_acl_c)
                                    
                permit_ICMP = 'permit icmp {} {} host {}'
                f_ICMP_c = permit_ICMP.format(ip, mask, ip)
                print(f_ICMP_c)

                permit_UDP1 = 'permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps'
                print(permit_UDP1)

                permit_UDP2 = 'permit udp {} {} eq bootpc host {} eq bootps'
                f_UDP2_c = permit_UDP2.format(ip, mask, ip)
                print(f_UDP2_c)

                deny_ANY = 'deny ip any host {} log-input'
                f_ANY_c = deny_ANY.format(ip)
                print(f_ANY_c)

                permit_IP = 'permit ip {} {} any'
                f_IP_c = permit_IP.format(ip, mask)
                print(f_IP_c)

                deny_ANY_Log = 'deny ip any any log-input'
                print(deny_ANY_Log)
            print('')
            print('conf t')
            for (Int, vlan) in itertools.zip_longest(finalInt, finalVlan):
                print('')
                interface_c = 'int {}'
                f_int_c = interface_c.format(Int)
                print(f_int_c)
                intAccessGroup_c = 'ip access-group DATA-VLAN_{} in'
                f_intAG_c = intAccessGroup_c.format(vlan)
                print(f_intAG_c)
            print('')
#Tkinter check to allow NA review of the ACL about to be applied            
            Review_ck = messagebox.askyesno("Question","Everything look good?")
            if Review_ck == True:
                
#Block that sends the ACL config through netmiko
                for (ip, mask, vlan) in itertools.zip_longest(finalIP, finalInverseMask, finalVlan):
                    acl_name_c = 'ip access-list extended DATA-VLAN_{}'
                    f_acl_c = acl_name_c.format(vlan)
                    send_acl_c = ch.send_config_set(f_acl_c, exit_config_mode=False)
                    print(send_acl_c)
                                        
                    permit_ICMP = 'permit icmp {} {} host {}'
                    f_ICMP_c = permit_ICMP.format(ip, mask, ip)
                    send_ICMP_c = ch.send_config_set(f_ICMP_c, exit_config_mode=False)
                    print(send_ICMP_c)

                    permit_UDP1 = 'permit udp host 0.0.0.0 eq bootpc host 255.255.255.255 eq bootps'
                    send_UDP1_c = ch.send_config_set(permit_UDP1, exit_config_mode=False)
                    print(send_UDP1_c)

                    permit_UDP2 = 'permit udp {} {} eq bootpc host {} eq bootps'
                    f_UDP2_c = permit_UDP2.format(ip, mask, ip)
                    send_UDP2_c = ch.send_config_set(f_UDP2_c, exit_config_mode=False)
                    print(send_UDP2_c)

                    deny_ANY = 'deny ip any host {} log-input'
                    f_ANY_c = deny_ANY.format(ip)
                    send_ANY_c = ch.send_config_set(f_ANY_c, exit_config_mode=False)
                    print(send_ANY_c)

                    permit_IP = 'permit ip {} {} any'
                    f_IP_c = permit_IP.format(ip, mask)
                    send_IP_c = ch.send_config_set(f_IP_c, exit_config_mode=False)
                    print(send_IP_c)

                    deny_ANY_Log = '5000 deny ip any any log-input'
                    send_deny_c = ch.send_config_set(deny_ANY_Log, exit_config_mode=False)
                    print(send_deny_c)

                for (Int, vlan) in itertools.zip_longest(finalInt, finalVlan):
                    interface_c = 'int {}'
                    f_int_c = interface_c.format(Int)
                    send_int_c = ch.send_config_set(f_int_c, exit_config_mode=False)
                    print(send_int_c)

                    intAccessGroup_c = 'ip access-group DATA-VLAN_{} in'
                    f_intAG_c = intAccessGroup_c.format(vlan)
                    send_intAG = ch.send_config_set(f_intAG_c, exit_config_mode=False)
                    print(send_intAG)

                ch.disconnect

                print('---------next-----------') 
                
            else:
                print('skipping device')
                            
        except(NetmikoTimeoutException, NetmikoAuthenticationException) as error: 
            print('{}: {}'.format(host, error))