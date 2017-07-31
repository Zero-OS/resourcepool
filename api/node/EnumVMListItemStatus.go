package node

type EnumVMListItemStatus string

const (
	EnumVMListItemStatusrunning       EnumVMListItemStatus = "running"
	EnumVMListItemStatushalted        EnumVMListItemStatus = "halted"
	EnumVMListItemStatuspaused        EnumVMListItemStatus = "paused"
	EnumVMListItemStatuserror         EnumVMListItemStatus = "error"
	EnumVMListItemStatusmigrating     EnumVMListItemStatus = "migrating"
	EnumVMListItemStatusdeploying     EnumVMListItemStatus = "deploying"
	EnumVMListItemStatusstarting      EnumVMListItemStatus = "starting"
	EnumVMListItemStatushalting       EnumVMListItemStatus = "halting"
	EnumVMListItemStatusnetworkKilled EnumVMListItemStatus = "networkKilled"
)
