package node

type EnumContainerListItemStatus string

const (
	EnumContainerListItemStatusrunning       EnumContainerListItemStatus = "running"
	EnumContainerListItemStatushalted        EnumContainerListItemStatus = "halted"
	EnumContainerListItemStatusnetworkKilled EnumContainerListItemStatus = "networkKilled"
)
