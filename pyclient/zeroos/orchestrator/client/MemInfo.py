"""
Auto-generated class for MemInfo
"""

from . import client_support


class MemInfo(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(active, available, buffers, cached, free, inactive, total, used, usedPercent, wired):
        """
        :type active: int
        :type available: int
        :type buffers: int
        :type cached: int
        :type free: int
        :type inactive: int
        :type total: int
        :type used: int
        :type usedPercent: float
        :type wired: int
        :rtype: MemInfo
        """

        return MemInfo(
            active=active,
            available=available,
            buffers=buffers,
            cached=cached,
            free=free,
            inactive=inactive,
            total=total,
            used=used,
            usedPercent=usedPercent,
            wired=wired,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'MemInfo'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'active'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.active = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'available'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.available = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'buffers'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.buffers = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'cached'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.cached = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'free'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.free = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'inactive'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.inactive = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'total'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.total = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'used'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.used = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'usedPercent'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.usedPercent = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'wired'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.wired = client_support.val_factory(val, datatypes)
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
