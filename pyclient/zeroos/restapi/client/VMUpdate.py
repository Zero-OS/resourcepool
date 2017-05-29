"""
Auto-generated class for VMUpdate
"""
from .NicLink import NicLink
from .VDiskLink import VDiskLink

from . import client_support


class VMUpdate(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(cpu, disks, memory, nics):
        """
        :type cpu: int
        :type disks: list[VDiskLink]
        :type memory: int
        :type nics: list[NicLink]
        :rtype: VMUpdate
        """

        return VMUpdate(
            cpu=cpu,
            disks=disks,
            memory=memory,
            nics=nics,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'VMUpdate'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'cpu'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.cpu = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'disks'
        val = data.get(property_name)
        if val is not None:
            datatypes = [VDiskLink]
            try:
                self.disks = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'memory'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.memory = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'nics'
        val = data.get(property_name)
        if val is not None:
            datatypes = [NicLink]
            try:
                self.nics = client_support.list_factory(val, datatypes)
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
