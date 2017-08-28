package vdisk

import (
	"gopkg.in/validator.v2"
)

type VdiskListItem struct {
	ID                   string                   `yaml:"id" json:"id" validate:"nonzero"`
	Status               EnumVdiskStatus          `yaml:"status" json:"status,omitempty"`
	BlockStoragecluster  string                   `yaml:"blockStoragecluster" json:"blockStoragecluster" validate:"nonzero"`
	ObjectStoragecluster string                   `yaml:"objectStoragecluster" json:"objectStoragecluster" validate:"nonzero"`
	BackupStoragecluster string                   `yaml:"backupStoragecluster" json:"backupStoragecluster" validate:"nonzero"`
	Vdisktype            EnumVdiskCreateVdisktype `yaml:"type" json:"type" validate:"nonzero"`
}

func (s VdiskListItem) Validate() error {

	return validator.Validate(s)
}
