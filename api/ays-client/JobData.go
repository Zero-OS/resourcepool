package client

import (
	"encoding/json"
	"gopkg.in/validator.v2"
)

type JobData struct {
	Data  json.RawMessage `json:"data" validate:"nonzero"`
	Jobid string          `json:"jobid" validate:"nonzero"`
	State string          `json:"state" validate:"nonzero"`
}

func (s JobData) Validate() error {

	return validator.Validate(s)
}
