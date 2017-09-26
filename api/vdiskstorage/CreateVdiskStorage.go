package vdiskstorage

import (
	"gopkg.in/validator.v2"
)

type CreateVdiskStorage struct {
	BlockCluster  string `json:"blockCluster" yaml:"blockCluster"  validate:"nonzero"`
	ObjectCluster string `json:"objectCluster" yaml:"objectCluster"`
	SlaveCluster  string `json:"slaveCluster" yaml:"slaveCluster"`
}

func (s CreateVdiskStorage) Validate() error {

	return validator.Validate(s)
}
