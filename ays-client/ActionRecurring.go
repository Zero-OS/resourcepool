package client

import (
	"gopkg.in/validator.v2"
)

type ActionRecurring struct {
	Last_run int `json:"last_run" validate:"nonzero"`
	Period   int `json:"period" validate:"nonzero"`
}

func (s ActionRecurring) Validate() error {

	return validator.Validate(s)
}
