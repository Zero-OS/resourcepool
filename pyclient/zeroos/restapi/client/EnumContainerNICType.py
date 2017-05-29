from enum import Enum


class EnumContainerNICType(Enum):
    zerotier = "zerotier"
    vxlan = "vxlan"
    vlan = "vlan"
    default = "default"
    bridge = "bridge"
