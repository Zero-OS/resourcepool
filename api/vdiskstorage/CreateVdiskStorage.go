package vdiskstorage

import (
	"gopkg.in/validator.v2"
)

type CreateVdiskStorage struct {
	BlockCluster  string `json:"blockCluster" yaml:"blockCluster"  validate:"nonzero"`
	ObjectCluster string `json:"objectCluster" yaml:"objectCluster" validate:"nonzero"`
	SlaveCluster  string `json:"slaveCluster" yaml:"slaveCluster" validate:"nonzero"`
}

func (s CreateVdiskStorage) Validate() error {

	return validator.Validate(s)
}
