package node

import (
	"gopkg.in/validator.v2"
)

// Node node in the g8os grid
type Node struct {
	Hostname  string         `json:"hostname" validate:"nonzero"`
	Id        string         `json:"id" validate:"nonzero"`
	IPAddress string         `json:"ipaddress" validate:"nonzero"`
	Status    EnumNodeStatus `json:"status" validate:"nonzero"`
	version   string         `json:"version" validate:"version"`
}

type NodeService struct {
	Node
	RedisAddr string `json:"redisAddr" validate:"nonzero"`
}

func (s Node) Validate() error {

	return validator.Validate(s)
}
