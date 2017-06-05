"""
Auto-generated class for VMDiskInfo
"""

from . import client_support


class VMDiskInfo(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(readIops, readThroughput, writeIops, writeThroughput):
        """
        :type readIops: int
        :type readThroughput: int
        :type writeIops: int
        :type writeThroughput: int
        :rtype: VMDiskInfo
        """

        return VMDiskInfo(
            readIops=readIops,
            readThroughput=readThroughput,
            writeIops=writeIops,
            writeThroughput=writeThroughput,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'VMDiskInfo'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'readIops'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.readIops = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'readThroughput'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.readThroughput = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'writeIops'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.writeIops = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'writeThroughput'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.writeThroughput = client_support.val_factory(val, datatypes)
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
