from enum import Enum


class EnumContainerListItemStatus(Enum):
    running = "running"
    halted = "halted"
    networkKilled = "networkKilled"
