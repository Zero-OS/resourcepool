package client

import (
	"gopkg.in/validator.v2"
)

type TemplateRecurringAction struct {
	Action string `json:"action" validate:"nonzero"`
	Log    bool   `json:"log"`
	Period string `json:"period" validate:"nonzero"`
}

func (s TemplateRecurringAction) Validate() error {

	return validator.Validate(s)
}
