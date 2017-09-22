package node

type EnumVMStatus string

const (
	EnumVMStatusrunning       EnumVMStatus = "running"
	EnumVMStatushalted        EnumVMStatus = "halted"
	EnumVMStatuspaused        EnumVMStatus = "paused"
	EnumVMStatushalting       EnumVMStatus = "halting"
	EnumVMStatusmigrating     EnumVMStatus = "migrating"
	EnumVMStatusdeploying     EnumVMStatus = "deploying"
	EnumVMStatuserror         EnumVMStatus = "error"
	EnumVMStatusstarting      EnumVMStatus = "starting"
	EnumVMStatusnetworkKilled EnumVMStatus = "networkKilled"
)
