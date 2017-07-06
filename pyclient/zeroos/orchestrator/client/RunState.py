from enum import Enum


class RunState(Enum):
    ok = "ok"
    running = "running"
    scheduled = "scheduled"
    error = "error"
    new = "new"
    disabled = "disabled"
    changed = "changed"
