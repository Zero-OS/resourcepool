package node

import (
	"fmt"
	"unicode/utf8"

	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type ExportVM struct {
	URL       string `yaml:"url" json:"url" validate:"nonzero"`
	CryptoKey string `yaml:"cryptoKey" json:"cryptoKey"`
}

func (s ExportVM) Validate() error {
	if err := validators.ValidateFtpURL(s.URL); err != nil {
		return err
	}

	if s.CryptoKey != "" && utf8.RuneCountInString(s.CryptoKey) != 32 {
		err := fmt.Errorf("The cryptoKey has a required fixed length of 32 bytes")
		return err
	}
	return validator.Validate(s)
}
