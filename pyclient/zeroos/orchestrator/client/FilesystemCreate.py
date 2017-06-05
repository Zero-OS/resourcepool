"""
Auto-generated class for FilesystemCreate
"""

from . import client_support


class FilesystemCreate(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(name, quota, readOnly):
        """
        :type name: str
        :type quota: int
        :type readOnly: bool
        :rtype: FilesystemCreate
        """

        return FilesystemCreate(
            name=name,
            quota=quota,
            readOnly=readOnly,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'FilesystemCreate'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

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

        property_name = 'quota'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.quota = client_support.val_factory(val, datatypes)
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
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
