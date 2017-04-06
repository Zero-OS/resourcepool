package client

import (
	"gopkg.in/validator.v2"
)

type Repository struct {
	Git_url string `json:"git_url" validate:"nonzero"`
	Name    string `json:"name" validate:"nonzero"`
	Path    string `json:"path" validate:"nonzero"`
}

func (s Repository) Validate() error {

	return validator.Validate(s)
}
