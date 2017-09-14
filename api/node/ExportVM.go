package node

import (
	"gopkg.in/validator.v2"
)

type ExportVM struct {
	URL string `yaml:"url" json:"url" validate:"nonzero"`
}

func (s ExportVM) Validate() error {
	return validator.Validate(s)
}
