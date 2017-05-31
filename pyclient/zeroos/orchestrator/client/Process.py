"""
Auto-generated class for Process
"""
from .CPUStats import CPUStats

from . import client_support


class Process(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(cmdline, cpu, pid, rss, swap, vms):
        """
        :type cmdline: str
        :type cpu: CPUStats
        :type pid: int
        :type rss: int
        :type swap: int
        :type vms: int
        :rtype: Process
        """

        return Process(
            cmdline=cmdline,
            cpu=cpu,
            pid=pid,
            rss=rss,
            swap=swap,
            vms=vms,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Process'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'cmdline'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.cmdline = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'cpu'
        val = data.get(property_name)
        if val is not None:
            datatypes = [CPUStats]
            try:
                self.cpu = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'pid'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.pid = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'rss'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.rss = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'swap'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.swap = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'vms'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.vms = client_support.val_factory(val, datatypes)
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
