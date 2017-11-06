package graph

import (
	"gopkg.in/validator.v2"
)

// Node node in the g8os grid
type GraphUpdate struct {
	URL string `json:"url"`
}

func (s GraphUpdate) Validate() error {

	return validator.Validate(s)
}
