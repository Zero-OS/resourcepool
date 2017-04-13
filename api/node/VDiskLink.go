package node

import (
	"gopkg.in/validator.v2"
)

// Definition of a virtual disk
type VDiskLink struct {
	MaxIOps  int    `json:"maxIOps" yaml:"maxIOps" validate:"nonzero"`
	Volumeid string `json:"volumeid" yaml:"volumeid" validate:"nonzero"`
}

func (s VDiskLink) Validate() error {

	return validator.Validate(s)
}
