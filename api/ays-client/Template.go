package client

import (
	"gopkg.in/validator.v2"
)

type Template struct {
	Actions string         `json:"actions" validate:"nonzero"`
	Config  TemplateConfig `json:"config" validate:"nonzero"`
	Name    string         `json:"name" validate:"nonzero"`
	Path    string         `json:"path" validate:"nonzero"`
	Role    string         `json:"role" validate:"nonzero"`
	Schema  string         `json:"schema" validate:"nonzero"`
}

func (s Template) Validate() error {

	return validator.Validate(s)
}
