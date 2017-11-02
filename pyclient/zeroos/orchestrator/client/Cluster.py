"""
Auto-generated class for Cluster
"""
from .EnumClusterDriveType import EnumClusterDriveType
from .EnumClusterStatus import EnumClusterStatus
from .StorageServer import StorageServer

from . import client_support


class Cluster(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(clusterType, driveType, label, nodes, status, storageServers):
        """
        :type clusterType: str
        :type driveType: EnumClusterDriveType
        :type label: str
        :type nodes: list[str]
        :type status: EnumClusterStatus
        :type storageServers: list[StorageServer]
        :rtype: Cluster
        """

        return Cluster(
            clusterType=clusterType,
            driveType=driveType,
            label=label,
            nodes=nodes,
            status=status,
            storageServers=storageServers,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Cluster'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'clusterType'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.clusterType = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'driveType'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumClusterDriveType]
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

        property_name = 'status'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumClusterStatus]
            try:
                self.status = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'storageServers'
        val = data.get(property_name)
        if val is not None:
            datatypes = [StorageServer]
            try:
                self.storageServers = client_support.list_factory(val, datatypes)
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
