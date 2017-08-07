package node

import (
	"gopkg.in/validator.v2"
)

type Container struct {
	Nics           []ContainerNIC      `json:"nics" validate:"nonzero"`
	Filesystems    []string            `json:"filesystems" validate:"nonzero"`
	Flist          string              `json:"flist" validate:"nonzero"`
	HostNetworking bool                `json:"hostNetworking" validate:"nonzero"`
	Hostname       string              `json:"hostname" validate:"nonzero"`
	Initprocesses  []CoreSystem        `json:"initprocesses" validate:"nonzero"`
	Ports          []string            `json:"ports" validate:"nonzero"`
	Status         EnumContainerStatus `json:"status" validate:"nonzero"`
	ZerotierNodeId string              `json:"zerotiernodeid,omitempty"`
	Storage        string              `json:"storage,omitempty"`
	Id             int                 `json:"id,omitempty"`
}

func (s Container) Validate() error {

	return validator.Validate(s)
}
