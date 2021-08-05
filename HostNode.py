class HostNode:

    __default = "NOT_DISCLOSED"  # if using default parameters for anything, the node is private (* in traceroute)

    def __init__(self,
                 private = True,
                 ip=__default,
                 hostname=__default,
                 city=__default,
                 region=__default,
                 coords=__default,
                 org=__default,
                 rtt=__default):
        self.__private = private
        self.__ip = ip
        self.__hostname = hostname
        self.__city = city
        self.__region = region
        self.__coords = coords
        self.__org = org
        self.__rtt = rtt  # add round trip time from parsed traceroute

    @property
    def private(self):
        return self.__private

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

    @property
    def rtt(self):
        return self.__rtt

    def dict(self):
        return {'private': self.private, 'ip': self.ip, 'hostname': self.hostname, 'city': self.city,
                'region': self.region, 'coords': self.coords, 'org': self.org, 'rtt': self.rtt}

    def __str__(self):
        if not self.private:
            return str(self.dict())
        else:
            return "device didn't respond, or timed out."

    def __repr__(self):
        return str(self.dict())
