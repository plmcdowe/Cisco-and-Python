
### <ins>Netmiko Documentation</ins>:
1. [ Netmiko GitHub ](https://github.com/ktbyers/netmiko)
2. [ Netmiko author's .io index ](https://ktbyers.github.io/netmiko/docs/netmiko/index.html)
3. [ Section covering Netmiko from ](https://python-automation-book.readthedocs.io/en/1.0/12_netmiko/01_netmiko.html) python-automation-book
4. [ Python For Net Eng's blog post ](https://pynet.twb-tech.com/blog/netmiko-python-library.html) with links to additional Netmiko documentation.

### [ 1 ][ ip_nestedDict.py ](https://github.com/plmcdowe/Cisco-and-Python/blob/60ce3fcb285e051494d1522b646fd5f53ba33fd0/ip_nestedDict.py)
> <b>It might not seem like it, but this is honestly the most important file here.</b></br>
> <b>It's a dictionary of nested lists that allows granular looping of specific device types from specific sites.</b></br>
> <b><ins>Here's the sanitized structure</ins>:</b>
> ```python
> remoteSites={
> 'SiteName1':[['RTR-IP'], ['SW1-IP', 'SW2-IP']],
> 'SiteName2':[['RTR-IP'], ['SW1-IP']],
> 'SiteName3':[['RTR-IP'], ['SW1-IP', 'SW2-IP', 'SW3-IP', 'SW4-IP']],
> 'SiteName4':[['RTR-IP'], ['SW1-IP']]
> }
> ```
> <b>Then, in each of the programs, pull the nested lists from the dictionary, then divide between switch and router.</b></br>
> <b><ins>Here's a snip of the structure in a router program to extract and loop routers</b></ins>:
> ```python
> from ip_nestedDict import remoteSites
> ls_sw=[]
> ls_rtr=[]
> ls_hosts=[] #nested lists of RTR/SWs per site, built from remoteSites dictionary
> 
> for key in remoteSites.keys():  #pulls out nested lists from dictionary
>     hosts = remoteSites[key]
>     ls_hosts.append(hosts)
> for list0, devices in enumerate(ls_hosts):   #enum list of sites
>     for list1, device in enumerate(devices): #enum list of devices per site
>         if list1!=0:
>             for list2, sw in enumerate(device): #enum lists of switches
>                 ls_sw.append(sw) #appends switch ips to list ls_sw
>         else:
>             for list2, rtr in enumerate(device): #enum lists of routers
>                 ls_rtr.append(rtr) #appends router ips to list ls_rtr
> for host in ls_rtr: #iterates string item (RTR IPs) as host for logging in
> }
> ```
> <ins>And here's a snip of the structure in a switch program to extract and loop switches</ins>:
> ```python
> from ip_nestedDict import remoteSites
> ls_sw=[]
> ls_rtr=[]
> ls_hosts=[] #nested lists of RTR/SWs per site, built from remoteSites dictionary
> 
> for key in remoteSites.keys():  #pulls out nested lists from dictionary
>     hosts = remoteSites[key]
>     ls_hosts.append(hosts)
> for list0, devices in enumerate(ls_hosts):   #enum list of sites
>     for list1, device in enumerate(devices): #enum list of devices per site
>         if list1!=0:
>             for list2, sw in enumerate(device): #enum lists of switches
>                 ls_sw.append(sw) #appends switch ips to list ls_sw
>         else:
>             for list2, rtr in enumerate(device): #enum lists of routers
>                 ls_rtr.append(rtr) #appends router ips to list ls_rtr
> for host in ls_rtr: #iterates string item (RTR IPs) as host for logging in
> }
> ```
### [ 2 ][ GuardRoot.py ](https://github.com/plmcdowe/Cisco-and-Python/blob/60ce3fcb285e051494d1522b646fd5f53ba33fd0/CISC-L2-000090_GuardRoot.py)
### [ 3 ][ SubINT-ACL.py ](https://github.com/plmcdowe/Cisco-and-Python/blob/60ce3fcb285e051494d1522b646fd5f53ba33fd0/CISC-RT-000130_SubINT-ACL.py)
### [ 4 ][ debug vpm all.py ](https://github.com/plmcdowe/Cisco-and-Python/blob/60ce3fcb285e051494d1522b646fd5f53ba33fd0/debug_vpm_all.py)
