package client

import (
	"gopkg.in/validator.v2"
)

type Job struct {
	Action_name  string `json:"action_name" validate:"nonzero"`
	Actor        string `json:"actor" validate:"nonzero"`
	Key          string `json:"key" validate:"nonzero"`
	Logs         []Log  `json:"logs" validate:"nonzero"`
	Service_key  string `json:"service_key" validate:"nonzero"`
	Service_name string `json:"service_name" validate:"nonzero"`
	State        string `json:"state" validate:"nonzero"`
}

func (s Job) Validate() error {

	return validator.Validate(s)
}
