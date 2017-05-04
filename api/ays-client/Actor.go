package client

import (
	"gopkg.in/validator.v2"
)

type Actor struct {
	Actions []Action `json:"actions" validate:"nonzero"`
	Name    string   `json:"name" validate:"nonzero"`
	Role    string   `json:"role" validate:"nonzero"`
	Schema  string   `json:"schema" validate:"nonzero"`
}

func (s Actor) Validate() error {

	return validator.Validate(s)
}
