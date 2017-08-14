from enum import Enum


class EnumVMStatus(Enum):
    deploying = "deploying"
    running = "running"
    halted = "halted"
    paused = "paused"
    halting = "halting"
    migrating = "migrating"
    starting = "starting"
    error = "error"
    networkKilled = "networkKilled"
