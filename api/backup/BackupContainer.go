package backup

import (
	"fmt"
	"net/url"
)

type BackupContainer struct {
	Name      string `json:"name"`
	Container string `json:"container"`
	URL       string `json:"url"`
}

func (s BackupContainer) Validate() error {
	if len(s.URL) == 0 {
		return fmt.Errorf("missing url")
	}

	_, err := url.Parse(s.URL)
	return err
}
