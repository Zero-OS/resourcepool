package storagecluster

import (
	"gopkg.in/validator.v2"
)

type StorageServer struct {
	Container string                  `yaml:"container" json:"container" validate:"nonzero"`
	ID        int                     `yaml:"id" json:"id" validate:"nonzero"`
	IP        string                  `yaml:"ip" json:"ip" validate:"nonzero"`
	Port      int                     `yaml:"port" json:"port" validate:"nonzero"`
	Status    EnumStorageServerStatus `yaml:"status" json:"status" validate:"nonzero"`
}

func (s StorageServer) Validate() error {

	return validator.Validate(s)
}
