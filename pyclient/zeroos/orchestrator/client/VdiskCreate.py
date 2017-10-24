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
    def create(blocksize, id, size, type, imageId=None, readOnly=None):
        """
        :type blocksize: int
        :type id: str
        :type imageId: str
        :type readOnly: bool
        :type size: int
        :type type: EnumVdiskCreateType
        :rtype: VdiskCreate
        """

        return VdiskCreate(
            blocksize=blocksize,
            id=id,
            imageId=imageId,
            readOnly=readOnly,
            size=size,
            type=type,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
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

        property_name = 'imageId'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.imageId = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

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
