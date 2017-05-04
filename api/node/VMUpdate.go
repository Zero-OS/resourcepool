package node

import (
	"gopkg.in/validator.v2"
)

type VMUpdate struct {
	Cpu             int         `json:"cpu" validate:"nonzero"`
	Disks           []VDiskLink `json:"disks"`
	Memory          int         `json:"memory" validate:"nonzero"`
	Nics            []NicLink   `json:"nics"`
}

func (s VMUpdate) Validate() error {
	return validator.Validate(s)
}
