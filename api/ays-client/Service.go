package client

import (
	"encoding/json"
	"gopkg.in/validator.v2"
)

type Service struct {
	Actions    []Action         `json:"actions" validate:"nonzero"`
	Actor      string           `json:"actor" validate:"nonzero"`
	Children   []ServicePointer `json:"children" validate:"nonzero"`
	Consumers  []ServicePointer `json:"consumers" validate:"nonzero"`
	Data       json.RawMessage  `json:"data" validate:"nonzero"`
	Events     []Event          `json:"events" validate:"nonzero"`
	Key        string           `json:"key" validate:"nonzero"`
	Name       string           `json:"name" validate:"nonzero"`
	Parent     ServicePointer   `json:"parent" validate:"nonzero"`
	Path       string           `json:"path" validate:"nonzero"`
	Producers  []ServicePointer `json:"producers" validate:"nonzero"`
	Repository string           `json:"repository" validate:"nonzero"`
	Role       string           `json:"role" validate:"nonzero"`
	State      string           `json:"state" validate:"nonzero"`
}

func (s Service) Validate() error {

	return validator.Validate(s)
}
