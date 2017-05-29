"""
Auto-generated class for VdiskListItem
"""
from .EnumVdiskListItemStatus import EnumVdiskListItemStatus
from .EnumVdiskListItemType import EnumVdiskListItemType

from . import client_support


class VdiskListItem(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(id, status, storagecluster, type):
        """
        :type id: str
        :type status: EnumVdiskListItemStatus
        :type storagecluster: str
        :type type: EnumVdiskListItemType
        :rtype: VdiskListItem
        """

        return VdiskListItem(
            id=id,
            status=status,
            storagecluster=storagecluster,
            type=type,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'VdiskListItem'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

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

        property_name = 'status'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumVdiskListItemStatus]
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

        property_name = 'type'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumVdiskListItemType]
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
