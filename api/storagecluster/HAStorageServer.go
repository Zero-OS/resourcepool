package storagecluster

import (
	"gopkg.in/validator.v2"
)

type HAStorageServer struct {
	Master *StorageServer `yaml:"master" json:"master" validate:"nonzero"`
	Slave  *StorageServer `yaml:"slave" json:"slave"`
}

func (s HAStorageServer) Validate() error {

	return validator.Validate(s)
}
