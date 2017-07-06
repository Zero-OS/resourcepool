"""
Auto-generated class for ContainerListItem
"""
from .EnumContainerListItemStatus import EnumContainerListItemStatus

from . import client_support


class ContainerListItem(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(flist, hostname, name, status):
        """
        :type flist: str
        :type hostname: str
        :type name: str
        :type status: EnumContainerListItemStatus
        :rtype: ContainerListItem
        """

        return ContainerListItem(
            flist=flist,
            hostname=hostname,
            name=name,
            status=status,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'ContainerListItem'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'flist'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.flist = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'hostname'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.hostname = client_support.val_factory(val, datatypes)
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
            datatypes = [EnumContainerListItemStatus]
            try:
                self.status = client_support.val_factory(val, datatypes)
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
