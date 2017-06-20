"""
Auto-generated class for StoragePool
"""
from .EnumStoragePoolDataProfile import EnumStoragePoolDataProfile
from .EnumStoragePoolMetadataProfile import EnumStoragePoolMetadataProfile
from .EnumStoragePoolStatus import EnumStoragePoolStatus

from . import client_support


class StoragePool(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(capacity, dataProfile, metadataProfile, mountpoint, name, status, totalCapacity):
        """
        :type capacity: int
        :type dataProfile: EnumStoragePoolDataProfile
        :type metadataProfile: EnumStoragePoolMetadataProfile
        :type mountpoint: str
        :type name: str
        :type status: EnumStoragePoolStatus
        :type totalCapacity: int
        :rtype: StoragePool
        """

        return StoragePool(
            capacity=capacity,
            dataProfile=dataProfile,
            metadataProfile=metadataProfile,
            mountpoint=mountpoint,
            name=name,
            status=status,
            totalCapacity=totalCapacity,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'StoragePool'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'capacity'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.capacity = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'dataProfile'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumStoragePoolDataProfile]
            try:
                self.dataProfile = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'metadataProfile'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumStoragePoolMetadataProfile]
            try:
                self.metadataProfile = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'mountpoint'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.mountpoint = client_support.val_factory(val, datatypes)
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

        property_name = 'status'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumStoragePoolStatus]
            try:
                self.status = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'totalCapacity'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.totalCapacity = client_support.val_factory(val, datatypes)
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
