"""
Auto-generated class for Vdisk
"""
from .EnumVdiskStatus import EnumVdiskStatus
from .EnumVdiskType import EnumVdiskType

from . import client_support


class Vdisk(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(blocksize, id, size, status, storagecluster, tlogStoragecluster, type, readOnly=None):
        """
        :type blocksize: int
        :type id: str
        :type readOnly: bool
        :type size: int
        :type status: EnumVdiskStatus
        :type storagecluster: str
        :type tlogStoragecluster: str
        :type type: EnumVdiskType
        :rtype: Vdisk
        """

        return Vdisk(
            blocksize=blocksize,
            id=id,
            readOnly=readOnly,
            size=size,
            status=status,
            storagecluster=storagecluster,
            tlogStoragecluster=tlogStoragecluster,
            type=type,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Vdisk'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'blocksize'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.blocksize = client_support.val_factory(val, datatypes)
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

        property_name = 'readOnly'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.readOnly = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

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

        property_name = 'status'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumVdiskStatus]
            try:
                self.status = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'storagecluster'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.storagecluster = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'tlogStoragecluster'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.tlogStoragecluster = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'type'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumVdiskType]
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
