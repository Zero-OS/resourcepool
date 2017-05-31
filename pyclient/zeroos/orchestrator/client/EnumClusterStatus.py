from enum import Enum


class EnumClusterStatus(Enum):
    empty = "empty"
    deploying = "deploying"
    ready = "ready"
    error = "error"
