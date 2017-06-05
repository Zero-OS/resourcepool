"""
Auto-generated class for BridgeCreateSetting
"""

from . import client_support


class BridgeCreateSetting(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(cidr, end, start):
        """
        :type cidr: str
        :type end: str
        :type start: str
        :rtype: BridgeCreateSetting
        """

        return BridgeCreateSetting(
            cidr=cidr,
            end=end,
            start=start,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'BridgeCreateSetting'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'cidr'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.cidr = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'end'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.end = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'start'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.start = client_support.val_factory(val, datatypes)
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
