package vdiskstorage

import (
	"gopkg.in/validator.v2"
)

// Import an image into a vdiskstorage
type ImageImport struct {
	Name            string `json:"imageName" validate:"nonzero,max=16"`
	ExportName      string `json:"exportName" validate:"nonzero"`
	ExportSnapshot  string `json:"exportSnapshot,omitempty"`
	Size            uint64 `json:"size" validate:"nonzero"`
	DiskBlockSize   uint64 `json:"diskBlockSize" validate:"nonzero"`
	ExportBlockSize uint64 `json:"exportBlockSize" validate:"nonzero"`
	URL             string `json:"url" validate:"nonzero"`
	EncryptionKey   string `json:"encryptionKey,omitempty"`
	Overwrite       bool   `json:"overwrite,omitempty"`
}

func (s ImageImport) Validate() error {

	return validator.Validate(s)
}
