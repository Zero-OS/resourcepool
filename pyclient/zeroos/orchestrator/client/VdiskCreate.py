"""
Auto-generated class for VdiskCreate
"""
from .EnumVdiskCreateType import EnumVdiskCreateType

from . import client_support


class VdiskCreate(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(blocksize, id, size, storagecluster, type, readOnly=None, templatevdisk=None, tlogStoragecluster=None):
        """
        :type blocksize: int
        :type id: str
        :type readOnly: bool
        :type size: int
        :type storagecluster: str
        :type templatevdisk: str
        :type tlogStoragecluster: str
        :type type: EnumVdiskCreateType
        :rtype: VdiskCreate
        """

        return VdiskCreate(
            blocksize=blocksize,
            id=id,
            readOnly=readOnly,
            size=size,
            storagecluster=storagecluster,
            templatevdisk=templatevdisk,
            tlogStoragecluster=tlogStoragecluster,
            type=type,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'VdiskCreate'
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

        property_name = 'templatevdisk'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.templatevdisk = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'tlogStoragecluster'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.tlogStoragecluster = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'type'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumVdiskCreateType]
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
