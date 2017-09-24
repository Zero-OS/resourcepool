package client

import (
	"gopkg.in/validator.v2"
)

type BlueprintListing struct {
	Name string `json:"name" validate:"nonzero"`
}

func (s BlueprintListing) Validate() error {

	return validator.Validate(s)
}
