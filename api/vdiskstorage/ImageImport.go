package vdiskstorage

import (
	"gopkg.in/validator.v2"
)

// Import an image into a vdiskstorage
type ImageImport struct {
	ID            string `json:"id" validate:"nonzero"`
	Size          uint64 `json:"size" validate:"nonzero"`
	BlockSize     uint64 `json:"blockSize" validate:"nonzero"`
	URL           string `json:"url" validate:"nonzero"`
	EncryptionKey string `json:"encryptionKey,omitempty"`
	Overwrite     bool   `json:"overwrite,omitempty"`
}

func (s ImageImport) Validate() error {

	return validator.Validate(s)
}
