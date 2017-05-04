package client

import (
	"gopkg.in/validator.v2"
)

type TemplateConfig struct {
	Links     []TemplateLink            `json:"links" validate:"nonzero"`
	Recurring []TemplateRecurringAction `json:"recurring" validate:"nonzero"`
}

func (s TemplateConfig) Validate() error {

	return validator.Validate(s)
}
