package node

import (
	"gopkg.in/validator.v2"
)

// Node node in the g8os grid
type Graph struct {
	URL string `json:"url,omitempty"`
	Id  string `json:"id,omitempty"`
}

type GraphService struct {
	Node string `json:"node" validate:"nonzero"`
	Port int    `json:"port" validate:"nonzero"`
	URL  string `json:"url"`
}

func (s Graph) Validate() error {

	return validator.Validate(s)
}
