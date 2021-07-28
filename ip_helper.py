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
	
	hostname = "www.google.com" 
	hostname = format_hostname(hostname)
	# CHECK IF HOSTNAME OR IP, also check if valid
	try:
		ip_addr  = socket.gethostbyname(hostname)
	except socket.gaierror:
		print("socket.gaierror: Check Internet Connection")
		sys.exit()
	
	
	print(get_ipinfo_node(ip_addr).city)
	
	print("running traceroute for {}".format(hostname))
	trace_res = os.popen("traceroute {}".format(hostname)).read()
	#print(trace_res)
	
	
	
	

	
	
