package client

import (
	"gopkg.in/validator.v2"
)

type AYSStep struct {
	Jobs   []Job  `json:"jobs" validate:"nonzero"`
	Number int    `json:"number" validate:"nonzero"`
	State  string `json:"state" validate:"nonzero"`
}

func (s AYSStep) Validate() error {

	return validator.Validate(s)
}
