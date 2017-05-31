"""
Auto-generated class for NicInfo
"""

from . import client_support


class NicInfo(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(addrs, flags, hardwareaddr, mtu, name):
        """
        :type addrs: list[str]
        :type flags: list[str]
        :type hardwareaddr: str
        :type mtu: int
        :type name: str
        :rtype: NicInfo
        """

        return NicInfo(
            addrs=addrs,
            flags=flags,
            hardwareaddr=hardwareaddr,
            mtu=mtu,
            name=name,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'NicInfo'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'addrs'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.addrs = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'flags'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.flags = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'hardwareaddr'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.hardwareaddr = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'mtu'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.mtu = client_support.val_factory(val, datatypes)
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

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
