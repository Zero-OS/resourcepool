from enum import Enum


class EnumNicLinkType(Enum):
    vlan = "vlan"
    vxlan = "vxlan"
    default = "default"
    bridge = "bridge"
