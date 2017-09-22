package healthcheck

import (
	"gopkg.in/validator.v2"
)

// Node node in the
type HealthCheck struct {
	ID         string    `json:"id" validate:"nonzero"`
	Name       string    `json:"name" validate:"nonzero"`
	Resource   string    `json:"resource" validate:"nonzero"`
	Messages   []Message `json:"messages" validate:"nonzero"`
	Category   string    `json:"category" validate:"nonzero"`
	LastTime   float32   `json:"lasttime" validate:"nonzero"`
	Interval   float32   `json:"interval" validate:"nonzero"`
	Stacktrace string    `json:"stacktrace" validate:"nonzero"`
}

type NodeHealthCheck struct {
	Hostname string `json:"hostname" validate:"nonzero"`
	ID       string `json:"id" validate:"nonzero"`
	Status   string `json:"status" validate:"nonzero"`
}

type StorageClusterHealthCheck struct {
	Label  string `yaml:"label" json:"label" validate:"nonzero"`
	Status string `yaml:"status" json:"status" validate:"nonzero"`
}

type Message struct {
	ID     string `json:"id" validate:"nonzero"`
	Status string `json:"status" validate:"nonzero"`
	Text   string `json:"text" validate:"nonzero"`
}

type Node struct {
	Hostname string `json:"hostname" validate:"nonzero"`
	ID       string `json:"id" validate:"nonzero"`
}

type StorageCluster struct {
	Label       string `json:"label" validate:"nonzero"`
	ClusterType string `json:"clusterType" validate:"nonzero"`
}

func (s HealthCheck) Validate() error {

	return validator.Validate(s)
}

// health/nodes
