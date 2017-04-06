package node

import (
	"gopkg.in/validator.v2"
)

// Arguments to create a new filesystem
type FilesystemCreate struct {
	Name     string `json:"name" validate:"nonzero"`
	Quota    uint32 `json:"quota"`
	ReadOnly bool   `json:"readOnly"`
}

func (s FilesystemCreate) Validate() error {

	return validator.Validate(s)
}
