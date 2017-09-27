package node

import (
	"gopkg.in/validator.v2"
	"github.com/zero-os/0-orchestrator/api/tools"
)

type VMCreate struct {
	Cpu    int         `json:"cpu" validate:"nonzero"`
	Disks  []VDiskLink `json:"disks"`
	Memory int         `json:"memory" validate:"nonzero"`
	Id     string      `json:"id" validate:"nonzero,servicename"`
	Nics   []NicLink   `json:"nics"`
}

func (s VMCreate) Validate(aysClient tools.AYStool, repoName string) error {
	for _, nic := range s.Nics {
		if err := nic.Validate(aysClient, repoName); err != nil {
			return err
		}
	}
	return validator.Validate(s)
}
