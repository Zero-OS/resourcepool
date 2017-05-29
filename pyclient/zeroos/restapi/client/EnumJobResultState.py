from enum import Enum


class EnumJobResultState(Enum):
    unknown_cmd = "unknown_cmd"
    error = "error"
    success = "success"
    killed = "killed"
    timeout = "timeout"
    duplicate_id = "duplicate_id"
    running = "running"
