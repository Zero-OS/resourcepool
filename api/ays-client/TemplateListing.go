package client

import (
	"gopkg.in/validator.v2"
)

type TemplateListing struct {
	Name string `json:"name" validate:"nonzero"`
}

func (s TemplateListing) Validate() error {

	return validator.Validate(s)
}
