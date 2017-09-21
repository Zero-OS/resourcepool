package client

import (
	"gopkg.in/validator.v2"
)

type NameListing struct {
	Name string `json:"name" validate:"nonzero"`
}

func (s NameListing) Validate() error {

	return validator.Validate(s)
}
