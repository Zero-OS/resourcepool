package vdiskstorage

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type VdiskStorage struct {
	BlockCluster  string `json:"blockCluster" yaml:"blockCluster"  validate:"nonzero"`
	ID            string `json:"id" yaml:"id" validate:"nonzero"`
	ObjectCluster string `json:"objectCluster" yaml:"objectCluster" validate:"nonzero"`
	SlaveCluster  string `json:"slaveCluster" yaml:"slaveCluster" validate:"nonzero"`
}

func (s VdiskStorage) Validate() error {

	if err := validators.ValidateVdiskStorage(s.ObjectCluster, s.SlaveCluster); err != nil {
		return err
	}
	return validator.Validate(s)

}
