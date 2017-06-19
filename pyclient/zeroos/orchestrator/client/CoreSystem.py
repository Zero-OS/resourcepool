"""
Auto-generated class for CoreSystem
"""

from . import client_support


class CoreSystem(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(name, args=None, environment=None, pwd=None, stdin=None):
        """
        :type args: list[str]
        :type environment: list[str]
        :type name: str
        :type pwd: str
        :type stdin: str
        :rtype: CoreSystem
        """

        return CoreSystem(
            args=args,
            environment=environment,
            name=name,
            pwd=pwd,
            stdin=stdin,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'CoreSystem'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'args'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.args = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'environment'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.environment = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

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

        property_name = 'pwd'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.pwd = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'stdin'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.stdin = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
