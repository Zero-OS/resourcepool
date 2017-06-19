"""
Auto-generated class for OSInfo
"""

from . import client_support


class OSInfo(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(bootTime, hostname, os, platform, platformFamily, platformVersion, procs, uptime, virtualizationRole, virtualizationSystem):
        """
        :type bootTime: int
        :type hostname: str
        :type os: str
        :type platform: str
        :type platformFamily: str
        :type platformVersion: str
        :type procs: int
        :type uptime: int
        :type virtualizationRole: str
        :type virtualizationSystem: str
        :rtype: OSInfo
        """

        return OSInfo(
            bootTime=bootTime,
            hostname=hostname,
            os=os,
            platform=platform,
            platformFamily=platformFamily,
            platformVersion=platformVersion,
            procs=procs,
            uptime=uptime,
            virtualizationRole=virtualizationRole,
            virtualizationSystem=virtualizationSystem,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'OSInfo'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'bootTime'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.bootTime = client_support.val_factory(val, datatypes)
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

        property_name = 'os'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.os = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'platform'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.platform = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'platformFamily'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.platformFamily = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'platformVersion'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.platformVersion = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'procs'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.procs = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'uptime'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.uptime = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'virtualizationRole'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.virtualizationRole = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'virtualizationSystem'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.virtualizationSystem = client_support.val_factory(val, datatypes)
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
