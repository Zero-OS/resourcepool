package ays

import (
	"fmt"
	"net/http"
	"strings"

	log "github.com/Sirupsen/logrus"
	client "github.com/zero-os/0-orchestrator/api/ays/ays-client"
)

// IsServiceExists test if a service exists
func (c *Client) IsServiceExists(role, name string) (bool, error) {
	_, resp, err := c.AYS().GetServiceByName(name, role, c.repo, nil, nil)
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
	return false, newError(resp, err)
}

// DeleteService deletes a service identify by role and name
func (c *Client) DeleteService(role, name string) error {
	resp, err := c.AYS().DeleteServiceByName(name, role, c.repo, nil, nil)
	return newError(resp, err)
}

// GetService is a shorthand function for getting a single service
func (c *Client) GetService(role, name, parent string, fields []string) (*client.Service, error) {
	opt := ListServiceOpt{
		Parent: parent,
		Fields: fields,
	}
	service, resp, err := c.AYS().GetServiceByName(name, role, c.repo, nil, opt.buildQuery())
	if err != nil || resp.StatusCode != http.StatusOK {
		return nil, newError(resp, err)
	}
	return service, nil
}

// ListServiceOpt is used to build queries to AYS
type ListServiceOpt struct {
	Parent  string
	Fields  []string
	Consume string
}

func (l *ListServiceOpt) buildQuery() map[string]interface{} {
	query := map[string]interface{}{}
	if l.Parent != "" {
		query["parent"] = l.Parent
	}
	if len(l.Fields) > 0 {
		query["fields"] = strings.Join(l.Fields, ",")
	}
	return query
}

// ListServices lists ays services using the role and ListServiceOpt query parameters
func (c *Client) ListServices(role string, opt ...ListServiceOpt) ([]*client.ServiceData, error) {
	var (
		services []*client.ServiceData
		resp     *http.Response
		err      error
	)

	if len(opt) <= 0 {
		services, resp, err = c.AYS().ListServicesByRole(role, c.repo, nil, nil)
	} else {
		services, resp, err = c.AYS().ListServicesByRole(role, c.repo, nil, opt[0].buildQuery())
	}
	log.Debugln(services)
	if err != nil || resp.StatusCode != http.StatusOK {
		return nil, newError(resp, err)
	}
	return services, nil
}
