"""
Auto-generated class for CPUInfo
"""

from . import client_support


class CPUInfo(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(cacheSize, cores, family, flags, mhz):
        """
        :type cacheSize: int
        :type cores: int
        :type family: str
        :type flags: list[str]
        :type mhz: float
        :rtype: CPUInfo
        """

        return CPUInfo(
            cacheSize=cacheSize,
            cores=cores,
            family=family,
            flags=flags,
            mhz=mhz,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'CPUInfo'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'cacheSize'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.cacheSize = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'cores'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.cores = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'family'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.family = client_support.val_factory(val, datatypes)
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

        property_name = 'mhz'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.mhz = client_support.val_factory(val, datatypes)
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
