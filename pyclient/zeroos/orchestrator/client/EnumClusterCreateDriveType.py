from enum import Enum


class EnumClusterCreateDriveType(Enum):
    nvme = "nvme"
    ssd = "ssd"
    hdd = "hdd"
    archive = "archive"
