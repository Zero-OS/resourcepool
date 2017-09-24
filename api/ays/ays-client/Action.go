package client

import (
	"gopkg.in/validator.v2"
)

type Action struct {
	Code      string          `json:"code" validate:"nonzero"`
	Name      string          `json:"name" validate:"nonzero"`
	Recurring ActionRecurring `json:"recurring" validate:"nonzero"`
	State     EnumActionState `json:"state" validate:"nonzero"`
}

func (s Action) Validate() error {

	return validator.Validate(s)
}
