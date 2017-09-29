package vdiskstorage

import (
	"gopkg.in/validator.v2"
)

// Vdisk image used as template for boot vdisks
type Image struct {
	Name      string `json:"name" validate:"nonzero"`
	Blocksize uint64 `json:"diskBlockSize" validate:"nonzero"`
	Size      uint64 `json:"size" validate:"nonzero"`
}

func (s Image) Validate() error {

	return validator.Validate(s)
}
