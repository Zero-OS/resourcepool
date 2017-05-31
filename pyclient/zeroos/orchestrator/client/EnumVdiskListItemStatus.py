from enum import Enum


class EnumVdiskListItemStatus(Enum):
    running = "running"
    halted = "halted"
    rollingback = "rollingback"
