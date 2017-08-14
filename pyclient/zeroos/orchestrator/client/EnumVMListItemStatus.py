from enum import Enum


class EnumVMListItemStatus(Enum):
    deploying = "deploying"
    running = "running"
    halted = "halted"
    paused = "paused"
    halting = "halting"
    migrating = "migrating"
    starting = "starting"
    error = "error"
    networkKilled = "networkKilled"
