package vdisk

import (
	"gopkg.in/validator.v2"
)

type VdiskCreate struct {
	ID                 string                     `yaml:"-" json:"id" validate:"nonzero"`
	Blocksize          int                        `yaml:"blocksize" json:"blocksize" validate:"nonzero"`
	ReadOnly           bool                       `yaml:"readOnly" json:"readOnly,omitempty"`
	Size               int                        `yaml:"size" json:"size" validate:"nonzero"`
	Storagecluster     string                     `yaml:"storagecluster" json:"storagecluster" validate:"nonzero"`
	Templatevdisk     string                     `yaml:"templatevdisk" json:"templatevdisk,omitempty"`
	TlogStoragecluster string                     `yaml:"tlogStoragecluster" json:"tlogStoragecluster,omitempty"`
	Vdisktype         EnumVdiskCreateVdisktype `yaml:"type" json:"type" validate:"nonzero"`
}

func (s VdiskCreate) Validate() error {

	return validator.Validate(s)
}
