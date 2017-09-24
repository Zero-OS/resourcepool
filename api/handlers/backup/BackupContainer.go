package backup

import (
	"net/url"

	"gopkg.in/validator.v2"
)

type BackupContainer struct {
	Name      string `json:"name" validate:"nonzero"`
	Container string `json:"container" validate:"nonzero"`
	URL       string `json:"url" validate:"nonzero"`
}

func (s BackupContainer) Validate() error {
	if err := validator.Validate(s); err != nil {
		return err
	}

	_, err := url.Parse(s.URL)
	return err
}
