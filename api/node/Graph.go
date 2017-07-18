package node

import (
	"gopkg.in/validator.v2"
)

// Node node in the g8os grid
type Graph struct {
	URL string `json:"url" validate:"nonzero"`
	Id  string `json:"id" validate:"nonzero"`
}

type GraphService struct {
	Node string `json:"node" validate:"nonzero"`
	Port int    `json:"port" validate:"nonzero"`
}

func (s Graph) Validate() error {

	return validator.Validate(s)
}
