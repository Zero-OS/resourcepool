"""
Auto-generated class for PortForward
"""
from .IPProtocol import IPProtocol

from . import client_support


class PortForward(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(dstip, dstport, protocols, srcip, srcport):
        """
        :type dstip: str
        :type dstport: int
        :type protocols: list[IPProtocol]
        :type srcip: str
        :type srcport: int
        :rtype: PortForward
        """

        return PortForward(
            dstip=dstip,
            dstport=dstport,
            protocols=protocols,
            srcip=srcip,
            srcport=srcport,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'PortForward'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'dstip'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.dstip = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'dstport'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.dstport = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'protocols'
        val = data.get(property_name)
        if val is not None:
            datatypes = [IPProtocol]
            try:
                self.protocols = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'srcip'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.srcip = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'srcport'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.srcport = client_support.val_factory(val, datatypes)
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
