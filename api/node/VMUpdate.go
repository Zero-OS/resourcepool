package node

import (
	"github.com/zero-os/0-orchestrator/api/tools"
	"gopkg.in/validator.v2"
)

type VMUpdate struct {
	Cpu    int         `json:"cpu" validate:"nonzero"`
	Disks  []VDiskLink `json:"disks"`
	Memory int         `json:"memory" validate:"nonzero"`
	Nics   []NicLink   `json:"nics"`
}

func (s VMUpdate) Validate(aysClient *tools.AYStool, repoName string) error {
	for _, nic := range s.Nics {
		if err := nic.Validate(aysClient, repoName); err != nil {
			return err
		}
	}
	return validator.Validate(s)
}
