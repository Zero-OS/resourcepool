package node

import (
	"gopkg.in/validator.v2"
)

type VMCreate struct {
	Cpu             int         `json:"cpu" validate:"nonzero"`
	Disks           []VDiskLink `json:"disks"`
	Memory          int         `json:"memory" validate:"nonzero"`
	Id              string      `json:"id" validate:"nonzero"`
	Nics            []NicLink   `json:"nics"`
	SystemCloudInit interface{} `json:"systemCloudInit"`
	UserCloudInit   interface{} `json:"userCloudInit"`
}

func (s VMCreate) Validate() error {
	return validator.Validate(s)
}
