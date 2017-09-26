package node

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
	"github.com/zero-os/0-orchestrator/api/tools"
)

type CreateContainer struct {
	Nics           []ContainerNIC `json:"nics"`
	Filesystems    []string       `json:"filesystems"`
	Flist          string         `json:"flist" validate:"nonzero"`
	HostNetworking bool           `json:"hostNetworking"`
	Hostname       string         `json:"hostname" validate:"nonzero"`
	Name           string         `json:"name" validate:"nonzero,servicename"`
	InitProcesses  []CoreSystem   `json:"initProcesses"`
	Ports          []string       `json:"ports"`
	Storage        string         `json:"storage"`
}

func (s CreateContainer) Validate(aysClient tools.AYStool, repoName string) error {
	for _, nic := range s.Nics {
		if err := nic.Validate(aysClient, repoName); err != nil {
			return err
		}
	}

	for _, fs := range s.Filesystems {
		if err := validators.ValidateContainerFilesystem(fs); err != nil {
			return err
		}
	}

	return validator.Validate(s)
}
