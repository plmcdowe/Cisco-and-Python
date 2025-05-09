### <b><ins>Netmiko Documentation</ins>:</b>
1. [ Netmiko GitHub ](https://github.com/ktbyers/netmiko)
2. [ Netmiko author's .io index ](https://ktbyers.github.io/netmiko/docs/netmiko/index.html)
3. [ Section covering Netmiko from ](https://python-automation-book.readthedocs.io/en/1.0/12_netmiko/01_netmiko.html) python-automation-book
4. [ Python For Net Eng's blog post ](https://pynet.twb-tech.com/blog/netmiko-python-library.html) with links to additional Netmiko documentation.

### [ 1 ] <ins>ip_nestedDict.py</ins>:</br>
> - <b>It might not seem like it, but [ip_nestedDict.py](https://github.com/plmcdowe/Cisco-and-Python/blob/60ce3fcb285e051494d1522b646fd5f53ba33fd0/ip_nestedDict.py) is honestly the most important file here.</b></br>
> - <b>It's a dictionary of nested lists that allows granular looping of specific device types from specific sites.</b></br>
>
> <b><ins>Here's the sanitized structure</ins>:</b>
>> ```python
>> remoteSites={
>> 'SiteName1':[['RTR-IP'], ['SW1-IP', 'SW2-IP']],
>> 'SiteName2':[['RTR-IP'], ['SW1-IP']],
>> 'SiteName3':[['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']],
>> 'SiteName4':[['RTR-IP'], ['SW1-IP']]
>> }
>> ```
> </br><b>Then, in a program, pull the nested lists from the dictionary, and store in switch or router list.</b></br>     
> <b><ins>Here's a snip of the structure in a router program to extract and loop routers</b></ins>:
>> ```python
>> from ip_nestedDict import remoteSites
>> ls_hosts=[] # nested lists of RTR/SWs per site, built from remoteSites dictionary
>> ls_rtr=[]   # list of routers built from ls_hosts
>> ls_sw=[]    # list of switches built from ls_hosts
>>
>> for key in remoteSites.keys(): # K:V (nested lists) of dictionary- 'SiteName3':[['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']],
>>     hosts = remoteSites[key]
>>     ls_hosts.append(hosts)
>> for list0, devices in enumerate(ls_hosts):   # enum lists of sites-            [['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']],
>>     for list1, device in enumerate(devices): # enum lists of devices per site-  ['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']
>>         if list1!=0: # list index is not 0 in list of lists                                 ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']
>>             for list2, sw in enumerate(device): # enum by switch in list of switches
>>                 ls_sw.append(sw) # append switch ips to list ls_sw
>>         else:
>>             for list2, rtr in enumerate(device): # enum lists of routers, index 0 per site
>>                 ls_rtr.append(rtr) # append rtr ips to list ls_rtr
>> # iterates router IPs as host from the router list
>> for host in ls_rtr:
>> ```
> <ins>And here's a snip of the structure in a switch program to extract and loop switches</ins>:
>> ```python
>> from ip_nestedDict import remoteSites
>> ls_hosts=[] # nested lists of RTR/SWs per site, built from remoteSites dictionary
>> ls_rtr=[]   # list of routers built from ls_hosts
>> ls_sw=[]    # list of switches built from ls_hosts
>>
>> for key in remoteSites.keys(): # K:V (nested lists) of dictionary- 'SiteName3':[['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']],
>>     hosts = remoteSites[key]
>>     ls_hosts.append(hosts)
>> for list0, devices in enumerate(ls_hosts):   # enum lists of sites-            [['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']],
>>     for list1, device in enumerate(devices): # enum lists of devices per site-  ['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']
>>         if list1!=0: # list index is not 0 in list of lists                                 ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']
>>             for list2, sw in enumerate(device): # enum by switch in list of switches
>>                 ls_sw.append(sw) # append switch ips to list ls_sw
>>         else:
>>             for list2, rtr in enumerate(device): # enum lists of routers, index 0 per site
>>                 ls_rtr.append(rtr)
>> # iterates switch IPs as host from the switch list
>> for host in ls_sw:
>> ```
>
> They're identical except for the last line: `for host in` 
> 
### [ 2 ] <ins>GuardRoot.py</ins>:</br>
> <b>[GuardRoot.py](https://github.com/plmcdowe/Cisco-and-Python/blob/60ce3fcb285e051494d1522b646fd5f53ba33fd0/CISC-L2-000090_GuardRoot.py)</b></br>

### [ 3 ] <ins>SubINT-ACL.py</ins>:</br>
> <b>[SubINT-ACL.py](https://github.com/plmcdowe/Cisco-and-Python/blob/78c7c2dd32831f862588519a2ff02dcc6bdc0402/CISC-RT-000130_SubINT-ACL.py)</b></br>

### [ 4 ] <ins>debug vpm all.py</ins>:</br>
> <b>[debug vpm all.py](https://github.com/plmcdowe/Cisco-and-Python/blob/78c7c2dd32831f862588519a2ff02dcc6bdc0402/debug_vpm_all.py)</b></br> 
