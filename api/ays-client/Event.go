package client

import (
	"gopkg.in/validator.v2"
)

type Event struct {
	Actions []string `json:"actions" validate:"nonzero"`
	Channel string   `json:"channel" validate:"nonzero"`
	Command string   `json:"command" validate:"nonzero"`
	Tags    []string `json:"tags" validate:"nonzero"`
}

func (s Event) Validate() error {

	return validator.Validate(s)
}
