import socket 			# for converting hostname to IP
import pycurl 			# for getting info about IP via ipinfo.io
import certifi 			# for HTTPS security with PycURL
import json				# for converting ipinfo.io result (json) to py dict
import os				# for running traceroute
import sys				# for exit on exception

from io import BytesIO 			# for buffer for pycurl to write into
from node_utils import HostNode, MissingInfoTypes  # class representing a host with info from ipinfo

def format_hostname(hostname): # UNIMPLEMENTED
	"""Format the hostname to only the host,
	e.g www.website.com/page12/option7 to www.website.com"""
	# also remove https?
	return hostname

def curl(url):
	buffer = BytesIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEDATA, buffer)
	c.setopt(c.CAINFO, certifi.where())
	c.perform()
	c.close

	bytes = buffer.getvalue()
	return bytes.decode('iso-8859-1')

def get_ipinfo_node(ip_addr, rtt):
	"""Takes an IPv4 address and uses ipinfo.io to get information in
	json format, and convert to python dictionary"""

	ipinfo_jsonstr = curl("https://ipinfo.io/"+ip_addr+"/json")
	ipinfo_dict = json.loads(ipinfo_jsonstr) # json.loads returns python dict

	return_dict = {} # ideally a clone of ipinfo_dict, but accounts for missing info (e.g no org) by filling in with 'NONE'
	keys = ["ip", "hostname", "city", "region", "loc", "org"]
	for key in keys:
		try:
			return_dict[key] = ipinfo_dict[key]
		except KeyError:
			return_dict[key] = MissingInfoTypes.NOT_PROVIDED

	ipinfo_dict = return_dict #REMOVE

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


	node_list = []

	try: # seperate into format function,
		ip_addr = socket.gethostbyname(hostname)  # might not actually need this!
	except socket.gaierror:
		print("socket.gaierror: Check Internet Connection")
		sys.exit()

	# print(get_ipinfo_node(ip_addr).city)

	print("running traceroute for {} using method {}".format(hostname, method.name))
	if method.name == "TCP" or method.name == "DCCP": # requires sudo
		if sudo_pass is None:
			print("error")
		else:
			result = os.popen("echo {} | sudo -S traceroute -M {} -n -q1 {}".format(sudo_pass, method.name, hostname))
	else:
		result = os.popen("traceroute -M {} -n -q1 {}".format(method.name, hostname))# .read() #.read() excluded as we want it in file format, not string
	result_lines = result.readlines()
	for line in result_lines[1:]:
		# skip first line (using [1:], as is not of index, key format
		# e.g: ("traceroute to www.google.com (172.217.169.68), 30 hops max, 60 byte packets")

		line = line.split("  ", maxsplit=1)
		i = line[0]
		content = line[1]
		if (content == "*\n"):
			node_list.append(HostNode(True))
			#print("device didn't respond, or timed out.")
		else:
			content = content.split("  ", maxsplit=1)
			ip = content[0]
			if (ip == "192.168.0.1"):
				ip = curl("ident.me") # get public address of your computer
			rtt = content[1].split("  ", maxsplit=1)[0]  # get the x from x ms # RTT DOESNT WORK
			rtt = rtt.split("\n")[0]  # remove \n
			node_list.append(get_ipinfo_node(ip, rtt))
			#print("{}, {} ({} : rtt={})".format(node.city, node.region, node.ip, rtt))

	return node_list


if __name__ == "__main__":

	# user enters hostname
	# perform traceroute
	# parse traceroute
	# make linked list of nodes for each IP in order
	# go through each node, from first to end: (first is user)
		# if not anon
			# plot on map
			# plot on flow
		# else
			# do not plot on map
			# plot anonymous on flow

	# CHECK IF HOSTNAME OR IP, also check if valid

	# further modularise?

	hostname = "www.w3schools.com" # gives weird output if use IP here
	hostname = format_hostname(hostname) # implement
	node_list = get_traceroute_node_list(hostname)

	for node in node_list:
		print("{}, {}".format(node.get_latitude(), node.get_longitude()))
		#print(repr(node))

	# allow options for ICMP, UDP












