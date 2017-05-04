package client

import (
	"gopkg.in/validator.v2"
)

type TemplateLink struct {
	Argname string `json:"argname" validate:"nonzero"`
	Auto    bool   `json:"auto"`
	Max     int    `json:"max" validate:"nonzero"`
	Min     int    `json:"min" validate:"nonzero"`
	Role    string `json:"role" validate:"nonzero"`
}

func (s TemplateLink) Validate() error {

	return validator.Validate(s)
}
