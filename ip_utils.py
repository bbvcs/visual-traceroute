import socket  # for converting hostname to IP
import pycurl  # for getting info about IP via ipinfo.io
import certifi  # for HTTPS security with PycURL
import json  # for converting ipinfo.io result (json) to py dict
import os  # for running traceroute
import sys  # for exit on exception
import re # for checking hostnames

from io import BytesIO  # for buffer for pycurl to write into
from node_utils import HostNode, MissingInfoTypes  # class representing a host with info from ipinfo


def format_hostname(hostname):  # UNIMPLEMENTED
    """Format the hostname to only the host,
    e.g https://www.website.com/page12/option7 to www.website.com"""

    hostname = hostname.lower()

    # does the hostname meet the standard straight away using RegEx? If so can return now.
    # (thanks to: https://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address)
    valid_hostname_regex = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    valid_hostname_checker = re.compile(valid_hostname_regex)
    match = valid_hostname_checker.match(hostname)
    if match:  # .match returns None on no match
        hostname = match.group() # or Match object on success, so need to extract

        if socket.gethostbyname(hostname) == hostname: # IPv4 addresses also pass regex above, as valid hostnames
            hostname = socket.gethostbyaddr(hostname)[0]  # then hostname is in IPv4 format, so convert to web address
        # this gethostby* call COULD throw socket.gaierror if not actual web addr, but valid format. handled by caller.
        return hostname

    # remove http / https:/
    if hostname[0] == 'h':
        # then we likely have http or https. (or, could be valid host beggining with 'h', e.g 'hello.com')
        if re.search("http://", hostname):
            hostname = hostname.split("http://")[1]
        elif re.search("https://", hostname):
            hostname = hostname.split("https://")[1]

    # so now we could still have www.website.com/page12/option7 left
    hostname = hostname.split("/")[0] # this should work, as no valid hostname will have / before a TLD

    return hostname


def curl(url):
    buffer = BytesIO()

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    c.perform()
    c.close()

    bytes = buffer.getvalue()
    return bytes.decode('iso-8859-1')


def generate_ipinfo_node(ip_addr, rtt):
    """Takes an IPv4 address and generates HostNode object, using ipinfo.io"""

    # get ipinfo of IP in dict form
    ipinfo_jsonstr = curl("https://ipinfo.io/" + ip_addr + "/json")
    ipinfo_dict = json.loads(ipinfo_jsonstr)  # json.loads returns python dict

    return_dict = {}  # ideally clone of ipinfo_dict, but accounts for missing info by filling in with 'NONE'
    keys = ["ip", "hostname", "city", "region", "loc", "org"]
    for key in keys:
        try:
            return_dict[key] = ipinfo_dict[key]
        except KeyError:
            return_dict[key] = MissingInfoTypes.NOT_PROVIDED

    ipinfo_dict = return_dict

    return HostNode(False,
                    ipinfo_dict["ip"],
                    ipinfo_dict["hostname"],
                    ipinfo_dict["city"],
                    ipinfo_dict["region"],
                    ipinfo_dict["loc"],
                    ipinfo_dict["org"],
                    rtt)


def get_traceroute_node_list(hostname, method, sudo_pass=None):
    """Runs traceroute for a hostname, putting every node (or a specified
    'firewall' value if unreachable) into a list"""

    try:
        hostname = format_hostname(hostname)
    except socket.gaierror as se:
        print("{}: Check Internet Connection".format(se))
        sys.exit()

    node_list = []

    print("\n\nrunning traceroute for {} using method {}".format(hostname, method.name))
    if method.name == "TCP" or method.name == "DCCP":  # requires sudo
        if sudo_pass is None:
            print("error")  # REPLACE WITH THROW
        else:
            result = os.popen("echo {} | sudo -S traceroute -M {} -n -q1 {}".format(sudo_pass, method.name, hostname))
    else:
        result = os.popen("traceroute -M {} -n -q1 {}".format(method.name, hostname))
    result_lines = result.readlines()
    for line in result_lines[1:]:
        # skip first line (using [1:], as is not of index, key format
        # e.g: ("traceroute to www.google.com (172.217.169.68), 30 hops max, 60 byte packets")

        line = line.split("  ", maxsplit=1)
        i = line[0]
        content = line[1]
        if (content == "*\n"):
            node_list.append(HostNode(True))
        # print("device didn't respond, or timed out.")
        else:
            content = content.split("  ", maxsplit=1)
            ip = content[0]
            if (ip == "192.168.0.1"): # WHAT IF OTHER LoCALS
                ip = curl("ident.me")  # get public address of your computer
            rtt = content[1].split("  ", maxsplit=1)[0]  # get the x from x ms # RTT DOESNT WORK
            rtt = rtt.split("\n")[0]  # remove \n
            node_list.append(generate_ipinfo_node(ip, rtt))
        # print("{}, {} ({} : rtt={})".format(node.city, node.region, node.ip, rtt))

    return node_list

if __name__ == "__main__":
    print(format_hostname("www.google.com"))
    print(format_hostname("https://www.google.com"))
    print(format_hostname("www.google.com/page1/page2"))
    print(format_hostname("https://www.google.com/page1/page2"))
    print(format_hostname("108.177.15.106"))