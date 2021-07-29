class HostNode:
	def __init__(self, ip, hostname, city, region, coords, org):
		self.__ip = ip
		self.__hostname = hostname
		self.__city = city
		self.__region = region
		self.__coords = coords
		self.__org = org
		#self.__rtt = rtt # add round trip time from parsed traceroute
	
	@property
	def city(self):
		return self.__city
