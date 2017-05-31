from enum import Enum


class EnumVdiskCreateType(Enum):
    boot = "boot"
    db = "db"
    cache = "cache"
    tmp = "tmp"
