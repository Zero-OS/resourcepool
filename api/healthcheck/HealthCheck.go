package healthcheck

import (
	"gopkg.in/validator.v2"
)

// Node node in the
type HealthCheck struct {
	ID       string `json:"id" validate:"nonzero"`
	Name     string `json:"name" validate:"nonzero"`
	Resource string `json:"resource" validate:"nonzero"`
	Status   string `json:"status" validate:"nonzero"`
	Message  string `json:"message" validate:"nonzero"`
}

type NodeHealthCheck struct {
	Hostname string `json:"hostname" validate:"nonzero"`
	ID       string `json:"id" validate:"nonzero"`
	Status   string `json:"status" validate:"nonzero"`
}

type Node struct {
	Hostname     string        `json:"hostname" validate:"nonzero"`
	ID           string        `json:"id" validate:"nonzero"`
	HealthChecks []HealthCheck `json:"healthchecks" validate:"nonzero"`
}

func (s HealthCheck) Validate() error {

	return validator.Validate(s)
}

// health/nodes
