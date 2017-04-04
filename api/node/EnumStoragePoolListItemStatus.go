package node

type EnumStoragePoolListItemStatus string

const (
	EnumStoragePoolListItemStatushealthy  EnumStoragePoolListItemStatus = "healthy"
	EnumStoragePoolListItemStatusdegraded EnumStoragePoolListItemStatus = "degraded"
	EnumStoragePoolListItemStatuserror    EnumStoragePoolListItemStatus = "error"
)
