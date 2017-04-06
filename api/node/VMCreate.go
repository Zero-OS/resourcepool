package node

import (
	"gopkg.in/validator.v2"
)

type VMCreate struct {
	Cpu    int         `json:"cpu" validate:"nonzero"`
	Disk   []VDiskLink `json:"disk" validate:"nonzero"`
	Memory int         `json:"memory" validate:"nonzero"`
	Name   string      `json:"name" validate:"nonzero"`
	Nic    []string    `json:"nic" validate:"nonzero"`
	//	SystemCloudInit object      `json:"systemCloudInit" validate:"nonzero"`
	//	UserCloudInit   object      `json:"userCloudInit" validate:"nonzero"`
}

func (s VMCreate) Validate() error {

	return validator.Validate(s)
}
