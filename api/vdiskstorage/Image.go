package vdiskstorage

import (
	"gopkg.in/validator.v2"
)

// Vdisk image used as template for boot vdisks
type Image struct {
	Blocksize uint64 `json:"blocksize" validate:"nonzero"`
	Id        string `json:"id" validate:"nonzero"`
	Size      uint64 `json:"size" validate:"nonzero"`
}

func (s Image) Validate() error {

	return validator.Validate(s)
}
