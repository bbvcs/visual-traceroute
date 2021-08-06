from enum import Enum, auto	    # for the NOT_DISCLOSED and NOT_PROVIDED types for information about a node


class MissingInfoTypes(Enum):
    """
    Used to represent node attributes that are for either reason not available:
        - NOT_DISCLOSED -> if node is private (i.e * in traceroute) then fields set to this
        - NOT_PROVIDED  -> if node provids info, but some fields are not provided (i.e gives IP, but not org)
    """
    NOT_DISCLOSED = auto()
    NOT_PROVIDED = auto()


class HostNode:
    """Represents a node - with attributes such as ip, coords etc - on the internet that is part of our trace route."""

    __default = MissingInfoTypes.NOT_DISCLOSED

    def __init__(self,
                 private = True, # private nodes do not reveal any info (i.e would be * in traceroute)
                 ip = __default,
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

    def get_latitude(self):  # N/S
        if self.coords == MissingInfoTypes.NOT_DISCLOSED:
            return MissingInfoTypes.NOT_DISCLOSED

        elif self.coords == MissingInfoTypes.NOT_PROVIDED:
            return MissingInfoTypes.NOT_PROVIDED

        return self.coords.split(',')[0]

    def get_longitude(self):  # E/W
        if self.coords == MissingInfoTypes.NOT_DISCLOSED:
            return MissingInfoTypes.NOT_DISCLOSED

        elif self.coords == MissingInfoTypes.NOT_PROVIDED:
            return MissingInfoTypes.NOT_PROVIDED

        return self.coords.split(',')[1]

    def __dict__(self):
        return {'private': self.private, 'ip': self.ip, 'hostname': self.hostname, 'city': self.city,
                'region': self.region, 'coords': self.coords, 'org': self.org, 'rtt': self.rtt}

    def __str__(self):
        if not self.private:
            copy = self.__dict__().copy()
            for attr in list(copy.values()):

                if attr == MissingInfoTypes.NOT_DISCLOSED:
                    attr = MissingInfoTypes.NOT_DISCLOSED.name

                elif attr == MissingInfoTypes.NOT_PROVIDED:
                    attr = MissingInfoTypes.NOT_PROVIDED.name

            return str(copy)
        else:
            return "device didn't respond, or timed out."

    def __repr__(self):
        return str(self.__dict__())
