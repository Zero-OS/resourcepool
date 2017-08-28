from enum import Enum


class EnumClusterCreateStorDriveType(Enum):
    nvme = "nvme"
    ssd = "ssd"
    hdd = "hdd"
    archive = "archive"
