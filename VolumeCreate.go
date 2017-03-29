package main

import (
	"gopkg.in/validator.v2"
)

type VolumeCreate struct {
	Blocksize      int    `json:"blocksize" validate:"nonzero"`
	Deduped        bool   `json:"deduped" validate:"nonzero"`
	Driver         string `json:"driver,omitempty"`
	ReadOnly       bool   `json:"readOnly,omitempty"`
	Size           int    `json:"size" validate:"nonzero"`
	Templatevolume string `json:"templatevolume,omitempty"`
}

func (s VolumeCreate) Validate() error {

	return validator.Validate(s)
}
