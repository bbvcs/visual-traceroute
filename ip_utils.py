import socket  # for converting hostname to IP
import pycurl  # for getting info about IP via ipinfo.io
import certifi  # for HTTPS security with PycURL
import json  # for converting ipinfo.io result (json) to py dict
import os  # for running traceroute
import sys  # for exit on exception
import re # for checking hostnames

from io import BytesIO  # for buffer for pycurl to write into

from node_utils import HostNode, MissingInfoTypes  # class representing a host with info from ipinfo


def format_hostname(hostname):
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

        try:
            if socket.gethostbyname(hostname) == hostname: # IPv4 addresses also pass regex above, as valid hostnames
                hostname = socket.gethostbyaddr(hostname)[0]  # then hostname is in IPv4 format, so convert to web address
            # this gethostby* call COULD throw socket.gaierror if not actual web addr, but valid format. handled by caller.
            return hostname
        except socket.herror:
            # TODO SHOW ALERT ETC
            print("")

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


def functions_correctly(result):
    """
        Return true if 'result' is the result of an os.popen() call, and that it 'worked' (the result of .readlines() > 0).

        I've moved this into a method as will be used a few times, AND I don't like the way I've done it; so want to
        easily change in the future.

        This method was made for when we use os.popen() for sudo traceoute; to check if we can use the sudo-only
        traceroute methods.
    """

    if str(type(result)) == "<class 'os._wrap_close'>" and len(result.readlines()) > 0:
        return True

    return False


def curl(url):
    """Returns String result of a pycurl call to url"""
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


def get_traceroute_node_list(hostname, method):
    """Runs traceroute for a hostname, putting every node (or a specified
    'firewall' value if unreachable) into a list"""

    try:
        hostname = format_hostname(hostname)
    except socket.gaierror as se:
        """ # TODO add this later, problematic currently becuause of circular import.
            # main.py should be seperated into main.py and class for GUI
        show_message_box("Requested Hostname Invalid",
                          "{}: Hostname Invalid or Internet Connection not available (check connection)".format(se)) """
        print("{}: Hostname Invalid or Internet Connection not available (check connection)".format(se))
        return
        #sys.exit()

    node_list = []

    print("\n\nrunning traceroute for {} using method {}".format(hostname, method.name))
    if method.name == "TCP" or method.name == "DCCP":  # these methods require sudo
        # pass not required as user sets up traceroute in visudo
        result = os.popen("sudo traceroute -M {} -n -q1 {}".format(method.name, hostname))
    else:  # could just do everything with call above, but want users who haven't setup traceroute in visudo to use non-sudo methods
        result = os.popen("traceroute -M {} -n -q1 {}".format(method.name, hostname))

    result_lines = result.readlines()

    print(len(result_lines)) # if 0 ...

    for line in result_lines[1:]:
        # skip first line (using [1:], as is not of index, key format
        # e.g: ("traceroute to www.google.com (172.217.169.68), 30 hops max, 60 byte packets")

        line = line.split("  ", maxsplit=1)
        content = line[1]  # for reference, line[0] would be a line index, we don't need it

        if content == "*\n":
            node_list.append(HostNode(private=True))  # node was unreachable, so represent as 'private' node
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
