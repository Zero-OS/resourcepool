from enum import Enum


class EnumDiskInfoType(Enum):
    ssd = "ssd"
    nvme = "nvme"
    hdd = "hdd"
    archive = "archive"
