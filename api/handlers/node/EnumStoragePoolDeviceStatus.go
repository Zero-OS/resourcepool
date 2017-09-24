package node

type EnumStoragePoolDeviceStatus string

const (
	EnumStoragePoolDeviceStatushealthy  EnumStoragePoolDeviceStatus = "healthy"
	EnumStoragePoolDeviceStatusremoving EnumStoragePoolDeviceStatus = "removing"
	EnumStoragePoolDeviceStatusdegraded EnumStoragePoolDeviceStatus = "degraded"
)
