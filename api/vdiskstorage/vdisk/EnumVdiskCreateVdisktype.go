package vdisk

type EnumVdiskCreateVdisktype string

const (
	EnumVdiskCreateVdisktypeboot  EnumVdiskCreateVdisktype = "boot"
	EnumVdiskCreateVdisktypedb    EnumVdiskCreateVdisktype = "db"
	EnumVdiskCreateVdisktypecache EnumVdiskCreateVdisktype = "cache"
	EnumVdiskCreateVdisktypetmp   EnumVdiskCreateVdisktype = "tmp"
)
