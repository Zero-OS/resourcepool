from enum import Enum


class EnumGWNICType(Enum):
    zerotier = "zerotier"
    vxlan = "vxlan"
    vlan = "vlan"
    default = "default"
    bridge = "bridge"
