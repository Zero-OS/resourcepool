package node

import (
	"gopkg.in/validator.v2"
)

type Container struct {
	Bridges        []Bridge            `json:"bridges" validate:"nonzero"`
	Filesystems    []string            `json:"filesystems" validate:"nonzero"`
	Flist          string              `json:"flist" validate:"nonzero"`
	HostNetworking bool                `json:"hostNetworking" validate:"nonzero"`
	Hostname       string              `json:"hostname" validate:"nonzero"`
	Id             string              `json:"id" validate:"nonzero"`
	Initprocesses  []CoreSystem        `json:"initprocesses" validate:"nonzero"`
	Ports          []string            `json:"ports" validate:"nonzero"`
	Status         EnumContainerStatus `json:"status" validate:"nonzero"`
	Zerotier       string              `json:"zerotier,omitempty"`
}

func (s Container) Validate() error {

	return validator.Validate(s)
}
