import socket 			# for converting hostname to IP
import pycurl 			# for getting info about IP via ipinfo.io
import certifi 			# for HTTPS security with PycURL
import json				# for converting ipinfo.io result (json) to py dict
import os				# for running traceroute
import sys				# for exit on exception

from io import BytesIO 			# for buffer for pycurl to write into
from HostNode import HostNode 	# class representing a host with info from ipinfo

def format_hostname(hostname): # UNIMPLEMENTED
	"""Format the hostname to only the host, 
	e.g www.website.com/page12/option7 to www.website.com"""
	# also remove https?
	return hostname 

def get_ipinfo_node(ip_addr):
	"""Takes an IPv4 address and uses ipinfo.io to get information in
	json format, and convert to python dictionary"""
	
	buffer = BytesIO()
	c = pycurl.Curl()
	c.setopt(c.URL, "https://ipinfo.io/"+ip_addr+"/json")
	c.setopt(c.WRITEDATA, buffer)
	c.setopt(c.CAINFO, certifi.where())
	c.perform()
	c.close

	ipinfo_bytes = buffer.getvalue()
	ipinfo_jsonstr = ipinfo_bytes.decode('iso-8859-1')
	ipinfo_dict = json.loads(ipinfo_jsonstr) # json.loads returns python dict

	return_dict = {} # ideally a clone of ipinfo_dict, but accounts for missing info (e.g no org) by filling in with 'NONE'
	keys = ["ip", "hostname", "city", "region", "loc", "org"]
	for key in keys:
		try:
			return_dict[key] = ipinfo_dict[key]
		except KeyError:
			return_dict[key] = "NONE"

	ipinfo_dict = return_dict #REMOVE

	return HostNode(ipinfo_dict["ip"],
					ipinfo_dict["hostname"],
					ipinfo_dict["city"],
					ipinfo_dict["region"],
					ipinfo_dict["loc"],
					ipinfo_dict["org"])

	
def get_info_for_traceroute_nodes(hostname):
	"""Runs traceroute for a hostname, putting every node (or a specified
	'firewall' value if unreachable) into a list, of type 'node'"""

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
		
	

	# further modularise?

	hostname = "www.google.com" 
	hostname = format_hostname(hostname) # implement
	# CHECK IF HOSTNAME OR IP, also check if valid
	try:
		ip_addr  = socket.gethostbyname(hostname) # might not actually need this!
	except socket.gaierror:
		print("socket.gaierror: Check Internet Connection")
		sys.exit()
	
	
	#print(get_ipinfo_node(ip_addr).city)
	
	
	
	print("running traceroute for {}".format(hostname))
	result = os.popen("traceroute -n -q1 {}".format(hostname))#.read() #.read() excluded as we want it in file format, not string
	result_lines = result.readlines()
	for line in result_lines[1:]: 
		# skip first line (using [1:], as is not of index, key format 
		# e.g: ("traceroute to www.google.com (172.217.169.68), 30 hops max, 60 byte packets")


		line = line.split("  ", maxsplit = 1)
		i = line[0]
		content = line[1]
		if (content == "*\n"):
			print("device didn't respond, or timed out.\n")
		else:
			content = content.split("  ", maxsplit=1)
			ip = content[0]
			rtt = content[1].split("  ", maxsplit=1)[0] # get the x from x ms # RTT DOESNT WORK
			rtt = rtt.split("\n")[0] # remove \n
			node = get_ipinfo_node(ip)
			print("{}, {} ({} : rtt={})\n".format(node.city, node.region, ip, rtt))

	
	
	
	
	

	
	
