package vdisk

type EnumVdiskStatus string

const (
	EnumVdiskStatusrunning     EnumVdiskStatus = "running"
	EnumVdiskStatushalted      EnumVdiskStatus = "halted"
	EnumVdiskStatusrollingback EnumVdiskStatus = "rollingback"
)
