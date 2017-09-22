package node

import (
	"gopkg.in/validator.v2"
)

type DiskPartition struct {
	Name     string `json:"name" validate:"nonzero"`
	Size     int    `json:"size" validate:"nonzero"`
	PartUUID string `json:"partuuid"`
	Label    string `json:"label"`
	FsType   string `json:"fstype"`
}

// Information about DiskInfo
type DiskInfo struct {
	Device     string           `json:"device" validate:"nonzero"`
	Size       int              `json:"size" validate:"nonzero"`
	Type       EnumDiskInfoType `json:"type" validate:"nonzero"`
	Partitions []DiskPartition  `json:"partitions"`
}

func (s DiskInfo) Validate() error {

	return validator.Validate(s)
}
