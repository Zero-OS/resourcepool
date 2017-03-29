package client

import (
	"gopkg.in/validator.v2"
)

type AYSRunListing struct {
	Epoch int                    `json:"epoch" validate:"nonzero"`
	Key   string                 `json:"key" validate:"nonzero"`
	State EnumAYSRunListingState `json:"state" validate:"nonzero"`
}

func (s AYSRunListing) Validate() error {

	return validator.Validate(s)
}
