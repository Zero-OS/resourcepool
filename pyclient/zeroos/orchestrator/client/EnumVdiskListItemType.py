from enum import Enum


class EnumVdiskListItemType(Enum):
    boot = "boot"
    db = "db"
    cache = "cache"
    tmp = "tmp"
