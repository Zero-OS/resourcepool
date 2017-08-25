"""
Auto-generated class for ClusterCreate
"""
from .EnumClusterCreateClusterType import EnumClusterCreateClusterType
from .EnumClusterCreateDriveType import EnumClusterCreateDriveType
from .EnumClusterCreateMetaDriveType import EnumClusterCreateMetaDriveType

from . import client_support


class ClusterCreate(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(clusterType, driveType, label, nodes, servers, dataShards=None, metaDriveType=None, parityShards=None):
        """
        :type clusterType: EnumClusterCreateClusterType
        :type dataShards: int
        :type driveType: EnumClusterCreateDriveType
        :type label: str
        :type metaDriveType: EnumClusterCreateMetaDriveType
        :type nodes: list[str]
        :type parityShards: int
        :type servers: int
        :rtype: ClusterCreate
        """

        return ClusterCreate(
            clusterType=clusterType,
            dataShards=dataShards,
            driveType=driveType,
            label=label,
            metaDriveType=metaDriveType,
            nodes=nodes,
            parityShards=parityShards,
            servers=servers,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'ClusterCreate'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'clusterType'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumClusterCreateClusterType]
            try:
                self.clusterType = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'dataShards'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.dataShards = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'driveType'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumClusterCreateDriveType]
            try:
                self.driveType = client_support.val_factory(val, datatypes)
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

        property_name = 'metaDriveType'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumClusterCreateMetaDriveType]
            try:
                self.metaDriveType = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'nodes'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.nodes = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'parityShards'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.parityShards = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'servers'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.servers = client_support.val_factory(val, datatypes)
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
