"""
Auto-generated class for GWNIC
"""
from .DHCP import DHCP
from .EnumGWNICType import EnumGWNICType

from . import client_support


class GWNIC(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(id, name, type, zerotierbridge, config=None, dhcpserver=None):
        """
        :type config: str
        :type dhcpserver: DHCP
        :type id: str
        :type name: str
        :type type: EnumGWNICType
        :type zerotierbridge: str
        :rtype: GWNIC
        """

        return GWNIC(
            config=config,
            dhcpserver=dhcpserver,
            id=id,
            name=name,
            type=type,
            zerotierbridge=zerotierbridge,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'GWNIC'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'config'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.config = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'dhcpserver'
        val = data.get(property_name)
        if val is not None:
            datatypes = [DHCP]
            try:
                self.dhcpserver = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'id'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.id = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

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

        property_name = 'type'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumGWNICType]
            try:
                self.type = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'zerotierbridge'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.zerotierbridge = client_support.val_factory(val, datatypes)
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
