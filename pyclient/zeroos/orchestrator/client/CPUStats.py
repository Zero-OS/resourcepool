"""
Auto-generated class for CPUStats
"""

from . import client_support


class CPUStats(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(guestNice, idle, ioWait, irq, nice, softIrq, steal, stolen, system, user):
        """
        :type guestNice: float
        :type idle: float
        :type ioWait: float
        :type irq: float
        :type nice: float
        :type softIrq: float
        :type steal: float
        :type stolen: float
        :type system: float
        :type user: float
        :rtype: CPUStats
        """

        return CPUStats(
            guestNice=guestNice,
            idle=idle,
            ioWait=ioWait,
            irq=irq,
            nice=nice,
            softIrq=softIrq,
            steal=steal,
            stolen=stolen,
            system=system,
            user=user,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'CPUStats'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'guestNice'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.guestNice = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'idle'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.idle = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'ioWait'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.ioWait = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'irq'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.irq = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'nice'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.nice = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'softIrq'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.softIrq = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'steal'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.steal = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'stolen'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.stolen = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'system'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.system = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'user'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.user = client_support.val_factory(val, datatypes)
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
