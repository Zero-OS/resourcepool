"""
Auto-generated class for HealthCheck
"""
from .Message import Message

from . import client_support


class HealthCheck(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(category, id, interval, lasttime, messages, name, resource, stacktrace):
        """
        :type category: str
        :type id: str
        :type interval: float
        :type lasttime: float
        :type messages: list[Message]
        :type name: str
        :type resource: str
        :type stacktrace: str
        :rtype: HealthCheck
        """

        return HealthCheck(
            category=category,
            id=id,
            interval=interval,
            lasttime=lasttime,
            messages=messages,
            name=name,
            resource=resource,
            stacktrace=stacktrace,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'HealthCheck'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'category'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.category = client_support.val_factory(val, datatypes)
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

        property_name = 'interval'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.interval = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'lasttime'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.lasttime = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'messages'
        val = data.get(property_name)
        if val is not None:
            datatypes = [Message]
            try:
                self.messages = client_support.list_factory(val, datatypes)
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

        property_name = 'resource'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.resource = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'stacktrace'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.stacktrace = client_support.val_factory(val, datatypes)
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
