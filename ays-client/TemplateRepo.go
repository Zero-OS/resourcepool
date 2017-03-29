package client

import (
	"gopkg.in/validator.v2"
)

type TemplateRepo struct {
	Branch string `json:"branch" validate:"nonzero"`
	Url    string `json:"url" validate:"nonzero"`
}

func (s TemplateRepo) Validate() error {

	return validator.Validate(s)
}
