package vdiskstorage

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type VdiskStorage struct {
	ID            string `json:"id" yaml:"id" validate:"nonzero"`
	BlockCluster  string `json:"blockCluster" yaml:"blockCluster"  validate:"nonzero"`
	ObjectCluster string `json:"objectCluster" yaml:"objectCluster"`
	SlaveCluster  string `json:"slaveCluster" yaml:"slaveCluster"`
}

func (s VdiskStorage) Validate() error {

	if err := validators.ValidateVdiskStorage(s.ObjectCluster, s.SlaveCluster); err != nil {
		return err
	}
	return validator.Validate(s)

}
