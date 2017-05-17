from enum import Enum


class EnumStoragePoolStatus(Enum):
    healthy = "healthy"
    degraded = "degraded"
    error = "error"
    unknown = "unknown"
