"""
Auto-generated class for DHCP
"""
from .GWHost import GWHost

from . import client_support


class DHCP(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(hosts, domain=None, nameservers=None):
        """
        :type domain: str
        :type hosts: list[GWHost]
        :type nameservers: list[str]
        :rtype: DHCP
        """

        return DHCP(
            domain=domain,
            hosts=hosts,
            nameservers=nameservers,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'DHCP'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'domain'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.domain = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'hosts'
        val = data.get(property_name)
        if val is not None:
            datatypes = [GWHost]
            try:
                self.hosts = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'nameservers'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.nameservers = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
