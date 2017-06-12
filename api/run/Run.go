package run

import (
	"gopkg.in/validator.v2"
)

type Run struct {
	Runid string `json:"runid" validate:"nonzero"`
	State string `json:"state" validate:"nonzero"`
}

func (s Run) Validate() error {

	return validator.Validate(s)
}
