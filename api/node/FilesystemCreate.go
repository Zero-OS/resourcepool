package node

import (
	"gopkg.in/validator.v2"
)

// Arguments to create a new filesystem
type FilesystemCreate struct {
	Name     string `yaml:"name" json:"name" validate:"nonzero,servicename"`
	Quota    uint32 `yaml:"quota" json:"quota"`
	ReadOnly bool   `yaml:"readOnly" json:"readOnly"`
}

func (s FilesystemCreate) Validate() error {

	return validator.Validate(s)
}
