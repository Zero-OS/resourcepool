package client

import (
	"gopkg.in/validator.v2"
)

type Log struct {
	Category string `json:"category" validate:"nonzero"`
	Epoch    int    `json:"epoch" validate:"nonzero"`
	Level    int    `json:"level" validate:"nonzero"`
	Log      string `json:"log" validate:"nonzero"`
	Tags     string `json:"tags" validate:"nonzero"`
}

func (s Log) Validate() error {

	return validator.Validate(s)
}
