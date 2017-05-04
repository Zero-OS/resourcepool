package node

import (
	"gopkg.in/validator.v2"
)

type VMCreate struct {
	Cpu             int         `json:"cpu" validate:"nonzero"`
	Disks           []VDiskLink `json:"disks"`
	Memory          int         `json:"memory" validate:"nonzero"`
	Id              string      `json:"id" validate:"nonzero,servicename"`
	Nics            []NicLink   `json:"nics"`
	SystemCloudInit interface{} `json:"systemCloudInit"`
	UserCloudInit   interface{} `json:"userCloudInit"`
}

func (s VMCreate) Validate() error {
	for _, nic := range s.Nics {
		if err := nic.Validate(); err != nil {
			return err
		}
	}
	return validator.Validate(s)
}
