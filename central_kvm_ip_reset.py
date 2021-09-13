#!/usr/bin/env python3

import requests
import getpass
import xml.etree.ElementTree as ET
from pprint import pprint
from urllib3.exceptions import InsecureRequestWarning


def central_login(auth_url, user, password):
    """This function performs UCS Central login and returns outCookie from response"""
    URL = auth_url
    payload = f"<aaaLogin inName={user} inPassword={password}/>"
    headers = {"Content-Type": "application/xml"}
    response = requests.request(
        "POST", url=URL, headers=headers, data=payload, verify=False
    )
    xml_root = ET.fromstring(response.content)
    outCookie = xml_root.attrib["outCookie"]
    return outCookie


def central_logout(outCookie, auth_url):
    """This function performs UCS Central Logout"""
    payload = f'<aaaLogout inCookie="{outCookie}"/>'
    headers = {"Content-Type": "application/xml"}
    response = requests.request(
        "POST", url=auth_url, headers=headers, data=payload, verify=False
    )
    xml_root = ET.fromstring(response.content)
    outStatus = xml_root.attrib["outStatus"]
    return outStatus


def get_all_orgs(outCookie, url):
    """This function returns all the Org DN's in UCS Central Domain"""
    payload = f'<configResolveClass\n  cookie="{outCookie}"\n  classId="orgOrg"\n  inHierarchical="false">\n  <inFilter>\n  </inFilter>\n</configResolveClass>'
    headers = {"Content-Type": "application/xml"}
    response = requests.request(
        "POST", url=url, headers=headers, data=payload, verify=False
    )
    xml_root = ET.fromstring(response.content)
    org_dict = {}
    for org in xml_root.iter("orgOrg"):
        org_name = org.attrib["name"]
        org_dn = org.attrib["dn"]
        org_dict[org_name] = org_dn
    return org_dict


def get_all_profiles(outCookie, url, org_dn):
    """This function gets all the profiles under an org and returns a profile dict with the profile name, dn and src_template"""
    payload = f'<configResolveChildren\ncookie="{outCookie}"\nclassId="lsServer"\ninDn="{org_dn}"\ninHierarchical="false">\n      <inFilter>\n    <eq class="lsServer" property="type" value="instance"/>\n  </inFilter>\n</configResolveChildren>'
    headers = {"Content-Type": "application/xml"}
    response = requests.request(
        "POST", url=url, headers=headers, data=payload, verify=False
    )
    xml_root = ET.fromstring(response.content)
    profile_dict = {}
    for server in xml_root.iter("lsServer"):
        profile_name = server.attrib["name"]
        profile_dn = server.attrib["dn"]
        profile_src_template = server.attrib["operSrcTemplName"]
        profile_dict[profile_name] = {
            "profile_dn": profile_dn,
            "src_template": profile_src_template,
        }
    return profile_dict


def get_profile_kvm_ip(outCookie, url, profile_dn):
    """This function returns a single profile KVM IP"""
    payload = f'<configResolveChildren\ncookie="{outCookie}"\nclassId="vnicIpV4PooledAddr"\ninDn="{profile_dn}"\ninHierarchical="false"\ninReturnCountOnly="false">\n    <inFilter>\n    </inFilter>\n</configResolveChildren>'
    headers = {"Content-Type": "application/xml"}
    response = requests.request(
        "POST", url=url, headers=headers, data=payload, verify=False
    )
    xml_root = ET.fromstring(response.content)
    # kvm_ip = xml_root[0][0].attrib["addr"]
    kvm_ip = ""
    for pool in xml_root.iter("vnicIpV4PooledAddr"):
        kvm_ip = pool.attrib["addr"]
    return kvm_ip


def reset_mgmt_ip(outCookie, url, profile_dn):
    """This function resets the Management IP on the provided profile"""
    print(f"Reset Management IP for profile: {profile_dn}")
    payload = f'<configRefreshIdentity\ndn="{profile_dn}"\ncookie="{outCookie}"\ninIdType="ipV4"\ninHierarchical="false">\n</configRefreshIdentity>'
    headers = {"Content-Type": "application/xml"}
    response = requests.request(
        "POST", url=url, headers=headers, data=payload, verify=False
    )
    xml_root = ET.fromstring(response.content)
    pprint(xml_root.attrib)


if __name__ == "__main__":
    # Suppress Certificate warnings
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    # Variable section
    ucs_central_ip = input("Please enter UCS Central IP: ")

    url = f"https://{ucs_central_ip}/xmlIM/central-mgr"
    auth_url = f"https://{ucs_central_ip}/xmlIM/"
    user = input("Please enter UCS Central User Name: ")
    password = getpass.getpass()

    # UCS Central Login and Get Auth Cookie
    print("")
    print("Getting Auth Cookie")
    outCookie = central_login(auth_url, user, password)
    print("")

    # Print Org DN
    print("We have the following Orgs in this Domain: ")
    org_dict = get_all_orgs(outCookie, url)
    for name, dn in org_dict.items():
        print(f"Org_Name: {name}, Org_Dn: {dn}")
    print("")

    # Get Profile Name, DN, Src_template
    org_dn = input(
        "Please enter Org DN from the above list E.g. org-root/org-child2/org-child21/org-child211 : "
    )
    print("Getting profile name, dn, src_template")
    profile_dict = get_all_profiles(outCookie, url, org_dn)
    print(f"Printing Profile_dict: {profile_dict}")
    print("")

    # Loop through the profile_dict and get the KVM IP of each profile and add profile dn, ip to kvm_ip_dict dictionary.
    print("Getting kvm-ip for each profile")
    if len(profile_dict) > 0:
        for profile in profile_dict.keys():
            profile_dn = profile_dict[profile]["profile_dn"]
            kvm_ip = get_profile_kvm_ip(outCookie, url, profile_dn)
            profile_dict[profile]["kvm_ip"] = kvm_ip
            # kvm_ip_dict[profile_dn] = kvm_ip
        print("")
        print("Printing profile_dict with KVM IPs")
        print(profile_dict)
        print("")

        # Loop through the kvm_ip_dict dictionary and if the KVM IP is 0.0.0.0, execute function reset_mgmt_ip
        print("Reset mgmt Ip if the kvm ip is 0.0.0.0")
        for profile in profile_dict.keys():
            if profile_dict[profile]["kvm_ip"] == "0.0.0.0":
                print(
                    f"Resetting Mgmt IP for {profile}, where kvm-ip is {profile_dict[profile]['kvm_ip']}"
                )
                profile_dn = profile_dict[profile]["profile_dn"]
                reset_mgmt_ip(outCookie, url, profile_dn)
            else:
                print(f"Skipping Profile: {profile}")
    else:
        print("No Profiles in this Org")

    # UCS Central Logout
    logout_status = central_logout(outCookie, auth_url)
    print("")
    print(f"Log Out of UCS Central: {logout_status}")
    print("")
