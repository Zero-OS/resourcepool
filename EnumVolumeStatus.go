package main

type EnumVolumeStatus string

const (
	EnumVolumeStatusrunning     EnumVolumeStatus = "running"
	EnumVolumeStatushalted      EnumVolumeStatus = "halted"
	EnumVolumeStatusrollingback EnumVolumeStatus = "rollingback"
)
