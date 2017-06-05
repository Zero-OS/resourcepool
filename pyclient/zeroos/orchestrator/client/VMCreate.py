"""
Auto-generated class for VMCreate
"""
from .NicLink import NicLink
from .VDiskLink import VDiskLink

from . import client_support


class VMCreate(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(cpu, disks, id, memory, nics, systemCloudInit, userCloudInit):
        """
        :type cpu: int
        :type disks: list[VDiskLink]
        :type id: str
        :type memory: int
        :type nics: list[NicLink]
        :type systemCloudInit: dict
        :type userCloudInit: dict
        :rtype: VMCreate
        """

        return VMCreate(
            cpu=cpu,
            disks=disks,
            id=id,
            memory=memory,
            nics=nics,
            systemCloudInit=systemCloudInit,
            userCloudInit=userCloudInit,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'VMCreate'
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

        property_name = 'systemCloudInit'
        val = data.get(property_name)
        if val is not None:
            datatypes = [dict]
            try:
                self.systemCloudInit = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'userCloudInit'
        val = data.get(property_name)
        if val is not None:
            datatypes = [dict]
            try:
                self.userCloudInit = client_support.val_factory(val, datatypes)
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
