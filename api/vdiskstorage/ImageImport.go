package vdiskstorage

import (
	"gopkg.in/validator.v2"
)

// Import an image into a vdiskstorage
type ImageImport struct {
	Name           string `json:"image_name" validate:"nonzero"`
	ExportName     string `json:"export_name" validate:"nonzero"`
	ExportSnapshot string `json:"export_snapshot,omitempty"`
	Size           uint64 `json:"size" validate:"nonzero"`
	BlockSize      uint64 `json:"blockSize" validate:"nonzero"`
	URL            string `json:"url" validate:"nonzero"`
	EncryptionKey  string `json:"encryptionKey,omitempty"`
	Overwrite      bool   `json:"overwrite,omitempty"`
}

func (s ImageImport) Validate() error {

	return validator.Validate(s)
}
