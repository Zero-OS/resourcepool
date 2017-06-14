package vdisk

import (
	"gopkg.in/validator.v2"
)

type VdiskRollback struct {
	Epoch uint64 `yaml:"epoch" json:"epoch" validate:"nonzero"`
}

func (s VdiskRollback) Validate() error {

	return validator.Validate(s)
}
