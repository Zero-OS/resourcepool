"""
Auto-generated class for GWHost
"""
from .CloudInit import CloudInit

from . import client_support


class GWHost(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(hostname, ipaddress, macaddress, cloudinit=None, ip6address=None):
        """
        :type cloudinit: CloudInit
        :type hostname: str
        :type ip6address: str
        :type ipaddress: str
        :type macaddress: str
        :rtype: GWHost
        """

        return GWHost(
            cloudinit=cloudinit,
            hostname=hostname,
            ip6address=ip6address,
            ipaddress=ipaddress,
            macaddress=macaddress,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'GWHost'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'cloudinit'
        val = data.get(property_name)
        if val is not None:
            datatypes = [CloudInit]
            try:
                self.cloudinit = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'hostname'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.hostname = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'ip6address'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.ip6address = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'ipaddress'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.ipaddress = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'macaddress'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.macaddress = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
