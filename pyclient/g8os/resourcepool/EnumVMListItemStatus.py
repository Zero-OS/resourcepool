from enum import Enum


class EnumVMListItemStatus(Enum):
    running = "running"
    halted = "halted"
    paused = "paused"
    error = "error"
