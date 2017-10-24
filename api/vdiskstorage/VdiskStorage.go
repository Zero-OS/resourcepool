package vdiskstorage

import (
	"fmt"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type VdiskStorage struct {
	ID            string `json:"id" yaml:"id" validate:"nonzero"`
	BlockCluster  string `json:"blockCluster" yaml:"blockCluster"  validate:"nonzero"`
	ObjectCluster string `json:"objectCluster" yaml:"objectCluster"`
	SlaveCluster  string `json:"slaveCluster" yaml:"slaveCluster"`
}

func (s VdiskStorage) Validate(aysClient *tools.AYStool, api *VdiskstorageAPI) error {
	// validate vdiskstorage name

	// validate block cluster name
	exists, err := aysClient.ServiceExists("storagecluster.block", s.BlockCluster, api.AysRepo)
	if err != nil {
		return err
	}
	if !exists {
		err = fmt.Errorf("storagecluster with name %s does not exists", s.BlockCluster)
		return err
	}

	// validate object cluster name
	if s.ObjectCluster != "" {
		exists, err = aysClient.ServiceExists("storagecluster.object", s.ObjectCluster, api.AysRepo)
		if err != nil {
			return err
		}
		if !exists {
			err = fmt.Errorf("storagecluster with name %s does not exists", s.ObjectCluster)
			return err
		}
		if s.SlaveCluster != "" {
			// validate slave cluster name
			exists, err = aysClient.ServiceExists("storagecluster.block", s.SlaveCluster, api.AysRepo)
			if err != nil {
				return err
			}
			if !exists {
				err = fmt.Errorf("storagecluster with name %s does not exists", s.SlaveCluster)
				return err
			}
		}
	}

	if err := validators.ValidateVdiskStorage(s.ObjectCluster, s.SlaveCluster); err != nil {
		return err
	}
	return validator.Validate(s)

}
