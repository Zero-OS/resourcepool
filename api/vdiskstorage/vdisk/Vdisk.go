package vdisk

import (
	"gopkg.in/validator.v2"
)

type Vdisk struct {
	Blocksize     int                `yaml:"blocksize" json:"blocksize" validate:"nonzero"`
	ID            string             `yaml:"id" json:"id" validate:"nonzero"`
	ReadOnly      bool               `yaml:"readOnly" json:"readOnly,omitempty"`
	Size          int                `yaml:"size" json:"size" validate:"nonzero"`
	Status        EnumVdiskStatus    `yaml:"status" json:"status" validate:"nonzero"`
	TemplateVdisk string             `yaml:"templatevdisk,omitempty" json:"templatevdisk,omitempty"`
	Vdiskstorage  string             `yaml:"vdiskstorage" json:"vdiskstorage" validate:"nonzero"`
	Vdisktype     EnumVdiskVdisktype `yaml:"type" json:"type" validate:"nonzero"`
}

func (s Vdisk) Validate() error {

	return validator.Validate(s)
}
