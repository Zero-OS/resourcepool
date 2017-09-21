package ays

import (
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
)

// IsServiceExists test if a service exists
func (c *Client) IsServiceExists(role, name string) (bool, error) {
	_, resp, err := c.client.Ays.GetServiceByName(name, role, c.repo, nil, nil)
	if err != nil {
		return false, newError(resp, err)
	}
	if resp.StatusCode == http.StatusOK {
		return true, nil
	}
	if resp.StatusCode == http.StatusNotFound {
		return false, nil
	}

	err = fmt.Errorf("AYS returned status %s while getting service", resp.Status)
	log.Error(err)
	return false, err
}
