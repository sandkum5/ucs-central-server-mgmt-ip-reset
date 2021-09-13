# ucs-central-server-mgmt-ip-reset
This scripts resets the UCS Central Server KVM Management IP


### Sample Run

```
% python3 central_kvm_ip_reset.py
Please enter UCS Central IP: 172.16.221.221
Please enter UCS Central User Name: admin
Password: 

Getting Auth Cookie

We have the following Orgs in this Domain: 
Org_Name: root, Org_Dn: org-root
Org_Name: child1, Org_Dn: org-root/org-child1
Org_Name: child11, Org_Dn: org-root/org-child1/org-child11
Org_Name: child2, Org_Dn: org-root/org-child2
Org_Name: child21, Org_Dn: org-root/org-child2/org-child21
Org_Name: child211, Org_Dn: org-root/org-child2/org-child21/org-child211

Please enter Org DN from the above list E.g. org-root/org-child2/org-child21/org-child211 : org-root/org-child2/org-child21/org-child211
Getting profile name, dn, src_template
Printing Profile_dict: {'temp2111': {'profile_dn': 'org-root/org-child2/org-child21/org-child211/ls-temp2111', 'src_template': 'org-root/org-child2/org-child21/org-child211/ls-temp211'}, 'temp2112': {'profile_dn': 'org-root/org-child2/org-child21/org-child211/ls-temp2112', 'src_template': 'org-root/org-child2/org-child21/org-child211/ls-temp211'}}

Getting kvm-ip for each profile

Printing profile_dict with KVM IPs
{'temp2111': {'profile_dn': 'org-root/org-child2/org-child21/org-child211/ls-temp2111', 'src_template': 'org-root/org-child2/org-child21/org-child211/ls-temp211', 'kvm_ip': '10.10.10.1'}, 'temp2112': {'profile_dn': 'org-root/org-child2/org-child21/org-child211/ls-temp2112', 'src_template': 'org-root/org-child2/org-child21/org-child211/ls-temp211', 'kvm_ip': '10.1.1.3'}}

Reset mgmt Ip if the kvm ip is 0.0.0.0
Skipping Profile: temp2111
Skipping Profile: temp2112

Log Out of UCS Central: success
```
