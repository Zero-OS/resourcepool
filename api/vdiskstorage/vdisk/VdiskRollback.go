package vdisk

import (
	"gopkg.in/validator.v2"
)

type VdiskRollback struct {
	Epoch int `yaml:"epoch" json:"epoch"`
}

func (s VdiskRollback) Validate() error {

	return validator.Validate(s)
}
