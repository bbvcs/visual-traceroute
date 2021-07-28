import socket 			# for converting hostname to IP
import pycurl 			# for getting info about IP via ipinfo.io
import certifi 			# for HTTPS security with PycURL
import json				# for converting ipinfo.io result (json) to py dict

from io import BytesIO 	# for buffer for pycurl to write into


def format_hostname(hostname): # UNIMPLEMENTED
	"""Format the hostname to only the host, 
	e.g www.website.com/page12/option7 to www.website.com"""
	
	return hostname 

def get_ipinfo_dict(ip_addr):
	"""Takes an IPv4 address and uses ipinfo.io to get information in
	json format, and convert to python dictionary"""
	
	buffer = BytesIO()
	c = pycurl.Curl()
	c.setopt(c.URL, "https://ipinfo.io/"+ip_addr+"/json")
	c.setopt(c.WRITEDATA, buffer)
	c.setopt(c.CAINFO, certifi.where())
	c.perform()
	c.close

	body = buffer.getvalue()
	json_format_str = body.decode('iso-8859-1')
	return json.loads(json_format_str) # json.loads returns python dict
	


if __name__ == "__main__":
	
	hostname = "www.google.com" 
	hostname = format_hostname(hostname)
	# CHECK IF HOSTNAME OR IP
	ip_addr  = socket.gethostbyname(hostname)
	
	print(type(get_ipinfo_dict(ip_addr)))
	

	
	
