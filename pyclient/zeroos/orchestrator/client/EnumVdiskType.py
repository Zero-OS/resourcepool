from enum import Enum


class EnumVdiskType(Enum):
    boot = "boot"
    db = "db"
    cache = "cache"
    tmp = "tmp"
