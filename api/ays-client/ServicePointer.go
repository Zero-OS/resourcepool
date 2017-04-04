package client

import (
	"gopkg.in/validator.v2"
)

type ServicePointer struct {
	Name string `json:"name" validate:"nonzero"`
	Role string `json:"role" validate:"nonzero"`
}

func (s ServicePointer) Validate() error {

	return validator.Validate(s)
}
