package node

import (
	"gopkg.in/validator.v2"
)

type Dashboard struct {
	Name      string `json:"name" validate:"nonzero,servicename,max=15"`
	Dashboard string `json:"dashboard" validate:"nonzero"`
}

func (s Dashboard) Validate() error {

	return validator.Validate(s)
}
