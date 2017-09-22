package node

type EnumContainerStatus string

const (
	EnumContainerStatusrunning       EnumContainerStatus = "running"
	EnumContainerStatushalted        EnumContainerStatus = "halted"
	EnumContainerStatusnetworkKilled EnumContainerStatus = "networkKilled"
)
