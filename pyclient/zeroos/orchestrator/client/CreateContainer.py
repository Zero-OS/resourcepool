"""
Auto-generated class for CreateContainer
"""
from .ContainerNIC import ContainerNIC
from .CoreSystem import CoreSystem

from . import client_support


class CreateContainer(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(flist, hostNetworking, hostname, name, filesystems=None, initProcesses=None, nics=None, ports=None, storage=None):
        """
        :type filesystems: list[str]
        :type flist: str
        :type hostNetworking: bool
        :type hostname: str
        :type initProcesses: list[CoreSystem]
        :type name: str
        :type nics: list[ContainerNIC]
        :type ports: list[str]
        :type storage: str
        :rtype: CreateContainer
        """

        return CreateContainer(
            filesystems=filesystems,
            flist=flist,
            hostNetworking=hostNetworking,
            hostname=hostname,
            initProcesses=initProcesses,
            name=name,
            nics=nics,
            ports=ports,
            storage=storage,
        )

    def __init__(self, json=None, **kwargs):
        if not json and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'CreateContainer'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'filesystems'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.filesystems = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

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

        property_name = 'hostNetworking'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.hostNetworking = client_support.val_factory(val, datatypes)
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

        property_name = 'initProcesses'
        val = data.get(property_name)
        if val is not None:
            datatypes = [CoreSystem]
            try:
                self.initProcesses = client_support.list_factory(val, datatypes)
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

        property_name = 'nics'
        val = data.get(property_name)
        if val is not None:
            datatypes = [ContainerNIC]
            try:
                self.nics = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'ports'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.ports = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'storage'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.storage = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
