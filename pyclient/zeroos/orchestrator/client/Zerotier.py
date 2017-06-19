"""
Auto-generated class for Zerotier
"""
from .EnumZerotierType import EnumZerotierType
from .ZerotierRoute import ZerotierRoute

from . import client_support


class Zerotier(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(allowDefault, allowGlobal, allowManaged, assignedAddresses, bridge, broadcastEnabled, dhcp, mac, mtu, name, netconfRevision, nwid, portDeviceName, portError, routes, status, type):
        """
        :type allowDefault: bool
        :type allowGlobal: bool
        :type allowManaged: bool
        :type assignedAddresses: list[str]
        :type bridge: bool
        :type broadcastEnabled: bool
        :type dhcp: bool
        :type mac: str
        :type mtu: int
        :type name: str
        :type netconfRevision: int
        :type nwid: str
        :type portDeviceName: str
        :type portError: int
        :type routes: list[ZerotierRoute]
        :type status: str
        :type type: EnumZerotierType
        :rtype: Zerotier
        """

        return Zerotier(
            allowDefault=allowDefault,
            allowGlobal=allowGlobal,
            allowManaged=allowManaged,
            assignedAddresses=assignedAddresses,
            bridge=bridge,
            broadcastEnabled=broadcastEnabled,
            dhcp=dhcp,
            mac=mac,
            mtu=mtu,
            name=name,
            netconfRevision=netconfRevision,
            nwid=nwid,
            portDeviceName=portDeviceName,
            portError=portError,
            routes=routes,
            status=status,
            type=type,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Zerotier'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'allowDefault'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.allowDefault = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'allowGlobal'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.allowGlobal = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'allowManaged'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.allowManaged = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'assignedAddresses'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.assignedAddresses = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'bridge'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.bridge = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'broadcastEnabled'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.broadcastEnabled = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'dhcp'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.dhcp = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'mac'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.mac = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'mtu'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.mtu = client_support.val_factory(val, datatypes)
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

        property_name = 'netconfRevision'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.netconfRevision = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'nwid'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.nwid = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'portDeviceName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.portDeviceName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'portError'
        val = data.get(property_name)
        if val is not None:
            datatypes = [int]
            try:
                self.portError = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'routes'
        val = data.get(property_name)
        if val is not None:
            datatypes = [ZerotierRoute]
            try:
                self.routes = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'status'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.status = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'type'
        val = data.get(property_name)
        if val is not None:
            datatypes = [EnumZerotierType]
            try:
                self.type = client_support.val_factory(val, datatypes)
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
