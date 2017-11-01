package client

import (
	"gopkg.in/validator.v2"
)

type AYSRun struct {
	Key     string     `json:"key" validate:"nonzero"`
	Retries RunRetries `json:"retries" validate:"nonzero"`
	State   string     `json:"state" validate:"nonzero"`
	Steps   []AYSStep  `json:"steps" validate:"nonzero"`
}

func (s AYSRun) Validate() error {

	return validator.Validate(s)
}
