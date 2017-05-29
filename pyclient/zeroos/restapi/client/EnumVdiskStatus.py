from enum import Enum


class EnumVdiskStatus(Enum):
    running = "running"
    halted = "halted"
    rollingback = "rollingback"
