import socket 			# for converting hostname to IP
import pycurl 			# for getting info about IP via ipinfo.io
import certifi 			# for HTTPS security with PycURL

from io import BytesIO 	# for buffer for pycurl to write into


def format_hostname(hostname): # UNIMPLEMENTED
	"""Format the hostname to only the host, 
	e.g www.website.com/page12/option7 to www.website.com"""
	return hostname 
	

if __name__ == "__main__":
	
	hostname = "www.google.com" # taken in as param probably
	hostname = format_hostname(hostname)
	# CHECK IF HOSTNAME OR IP
	ip_addr  = socket.gethostbyname(hostname)
	

	buffer = BytesIO()
	c = pycurl.Curl()
	c.setopt(c.URL, "https://ipinfo.io/"+ip_addr+"/json")
	c.setopt(c.WRITEDATA, buffer)
	c.setopt(c.CAINFO, certifi.where())
	c.perform()
	c.close

	body = buffer.getvalue()
	print(body.decode('iso-8859-1'))
