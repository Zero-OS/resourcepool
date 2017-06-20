"""
Auto-generated class for ListGW
"""
from .GWNIC import GWNIC
from .HTTPProxy import HTTPProxy
from .PortForward import PortForward

from . import client_support


class ListGW(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(domain, name, nics, httpproxies=None, portforwards=None, zerotiernodeid=None):
        """
        :type domain: str
        :type httpproxies: list[HTTPProxy]
        :type name: str
        :type nics: list[GWNIC]
        :type portforwards: list[PortForward]
        :type zerotiernodeid: str
        :rtype: ListGW
        """

        return ListGW(
            domain=domain,
            httpproxies=httpproxies,
            name=name,
            nics=nics,
            portforwards=portforwards,
            zerotiernodeid=zerotiernodeid,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'ListGW'
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
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'httpproxies'
        val = data.get(property_name)
        if val is not None:
            datatypes = [HTTPProxy]
            try:
                self.httpproxies = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'name'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.name = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'nics'
        val = data.get(property_name)
        if val is not None:
            datatypes = [GWNIC]
            try:
                self.nics = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'portforwards'
        val = data.get(property_name)
        if val is not None:
            datatypes = [PortForward]
            try:
                self.portforwards = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'zerotiernodeid'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.zerotiernodeid = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
