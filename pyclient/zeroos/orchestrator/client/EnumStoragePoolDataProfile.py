from enum import Enum


class EnumStoragePoolDataProfile(Enum):
    raid0 = "raid0"
    raid1 = "raid1"
    raid5 = "raid5"
    raid6 = "raid6"
    raid10 = "raid10"
    dup = "dup"
    single = "single"
