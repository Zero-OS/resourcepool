package node

import (
	"gopkg.in/validator.v2"
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

func (s CreateContainer) Validate() error {

	return validator.Validate(s)
}
