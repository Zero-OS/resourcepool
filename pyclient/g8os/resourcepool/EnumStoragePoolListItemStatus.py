from enum import Enum


class EnumStoragePoolListItemStatus(Enum):
    healthy = "healthy"
    degraded = "degraded"
    error = "error"
    unknown = "unknown"
