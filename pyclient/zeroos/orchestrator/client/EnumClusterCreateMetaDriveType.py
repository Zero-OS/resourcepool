from enum import Enum


class EnumClusterCreateMetaDriveType(Enum):
    nvme = "nvme"
    ssd = "ssd"
    hdd = "hdd"
    archive = "archive"
