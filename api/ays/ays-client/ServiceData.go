package client

import (
	"encoding/json"
	"gopkg.in/validator.v2"
)

type ServiceData struct {
	Data json.RawMessage `json:"data" validate:"nonzero"`
	Name string          `json:"name" validate:"nonzero"`
	Role string          `json:"role" validate:"nonzero"`
}

func (s ServiceData) Validate() error {

	return validator.Validate(s)
}
