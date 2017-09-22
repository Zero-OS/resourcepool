package node

import (
	"gopkg.in/validator.v2"
)

type VMMigrate struct {
	Nodeid string `json:"nodeid" validate:"nonzero,servicename"`
}

func (s VMMigrate) Validate() error {

	return validator.Validate(s)
}
