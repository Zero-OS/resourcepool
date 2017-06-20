"""
Auto-generated class for DiskInfo
"""
from .DiskPartition import DiskPartition
from .EnumDiskInfoType import EnumDiskInfoType

from . import client_support


class DiskInfo(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(device, partitions, size, type):
        """
        :type device: str
        :type partitions: list[DiskPartition]
        :type size: int
        :type type: EnumDiskInfoType
        :rtype: DiskInfo
        """

        return DiskInfo(
            device=device,
            partitions=partitions,
            size=size,
            type=type,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'DiskInfo'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'device'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.device = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'partitions'
        val = data.get(property_name)
        if val is not None:
            datatypes = [DiskPartition]
            try:
                self.partitions = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'size'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.size = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'type'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumDiskInfoType]
            try:
                self.type = client_support.val_factory(val, datatypes)
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
