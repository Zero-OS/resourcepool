package node

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type ExportVM struct {
	URL string `yaml:"url" json:"url" validate:"nonzero"`
}

func (s ExportVM) Validate() error {
	if err := validators.ValidateFtpURL(s.URL); err != nil {
		return err
	}
	return validator.Validate(s)
}
