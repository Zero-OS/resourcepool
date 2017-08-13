from enum import Enum


class EnumContainerStatus(Enum):
    running = "running"
    halted = "halted"
    networkKilled = "networkKilled"
