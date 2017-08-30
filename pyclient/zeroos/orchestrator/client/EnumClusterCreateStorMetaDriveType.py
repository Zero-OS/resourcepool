from enum import Enum


class EnumClusterCreateStorMetaDriveType(Enum):
    nvme = "nvme"
    ssd = "ssd"
    hdd = "hdd"
    archive = "archive"
