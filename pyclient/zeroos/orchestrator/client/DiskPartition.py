"""
Auto-generated class for DiskPartition
"""

from . import client_support


class DiskPartition(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(fstype, label, name, partuuid, size):
        """
        :type fstype: str
        :type label: str
        :type name: str
        :type partuuid: str
        :type size: int
        :rtype: DiskPartition
        """

        return DiskPartition(
            fstype=fstype,
            label=label,
            name=name,
            partuuid=partuuid,
            size=size,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'DiskPartition'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'fstype'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.fstype = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'label'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.label = client_support.val_factory(val, datatypes)
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

        property_name = 'partuuid'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.partuuid = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

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

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
