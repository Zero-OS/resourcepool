package node

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type ImportVM struct {
	URL                  string `yaml:"url" json:"url" validate:"nonzero"`
	BlockStoragecluster  string `yaml:"blockStoragecluster" json:"blockStoragecluster" validate:"nonzero"`
	ObjectStoragecluster string `yaml:"objectStoragecluster" json:"objectStoragecluster"`
	BackupStoragecluster string `yaml:"backupStoragecluster" json:"backupStoragecluster"`
}

func (s ImportVM) Validate() error {
	if err := validators.ValidateFtpURL(s.URL); err != nil {
		return err
	}

	return validator.Validate(s)
}
