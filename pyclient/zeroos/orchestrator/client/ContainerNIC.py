"""
Auto-generated class for ContainerNIC
"""
from .ContainerNICconfig import ContainerNICconfig
from .EnumContainerNICStatus import EnumContainerNICStatus
from .EnumContainerNICType import EnumContainerNICType

from . import client_support


class ContainerNIC(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(id, status, type, config=None, hwaddr=None, name=None, token=None):
        """
        :type config: ContainerNICconfig
        :type hwaddr: str
        :type id: str
        :type name: str
        :type status: EnumContainerNICStatus
        :type token: str
        :type type: EnumContainerNICType
        :rtype: ContainerNIC
        """

        return ContainerNIC(
            config=config,
            hwaddr=hwaddr,
            id=id,
            name=name,
            status=status,
            token=token,
            type=type,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'ContainerNIC'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'config'
        val = data.get(property_name)
        if val is not None:
            datatypes = [ContainerNICconfig]
            try:
                self.config = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'hwaddr'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.hwaddr = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

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

        property_name = 'name'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.name = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'status'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumContainerNICStatus]
            try:
                self.status = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'token'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.token = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'type'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumContainerNICType]
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
