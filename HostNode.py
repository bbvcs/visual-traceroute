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
	def ip(self):
		return self.__ip

	@property
	def hostname(self):
		return self.__hostname

	@property
	def city(self):
		return self.__city

	@property
	def region(self):
		return self.__region

	@property
	def coords(self):
		return self.__coords

	@property
	def org(self):
		return self.__org
