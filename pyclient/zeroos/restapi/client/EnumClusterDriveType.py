from enum import Enum


class EnumClusterDriveType(Enum):
    nvme = "nvme"
    ssd = "ssd"
    hdd = "hdd"
    archive = "archive"
