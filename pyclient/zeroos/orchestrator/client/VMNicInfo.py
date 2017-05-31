"""
Auto-generated class for VMNicInfo
"""

from . import client_support


class VMNicInfo(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(receivedPackets, receivedThroughput, transmittedPackets, transmittedThroughput):
        """
        :type receivedPackets: int
        :type receivedThroughput: int
        :type transmittedPackets: int
        :type transmittedThroughput: int
        :rtype: VMNicInfo
        """

        return VMNicInfo(
            receivedPackets=receivedPackets,
            receivedThroughput=receivedThroughput,
            transmittedPackets=transmittedPackets,
            transmittedThroughput=transmittedThroughput,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'VMNicInfo'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'receivedPackets'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.receivedPackets = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'receivedThroughput'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.receivedThroughput = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'transmittedPackets'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.transmittedPackets = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'transmittedThroughput'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.transmittedThroughput = client_support.val_factory(val, datatypes)
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
