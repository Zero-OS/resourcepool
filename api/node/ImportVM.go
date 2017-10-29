package node

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type ImportVM struct {
	URL          string `yaml:"url" json:"url" validate:"nonzero"`
	ID           string `yaml:"id" json:"id" validate:"nonzero"`
	VdiskStorage string `yaml:"vdiskstorage" json:"vdiskstorage" validate:"nonzero"`
}

func (s ImportVM) Validate() error {
	if err := validators.ValidateFtpURL(s.URL); err != nil {
		return err
	}

	return validator.Validate(s)
}
