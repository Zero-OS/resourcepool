package client

import (
	"gopkg.in/validator.v2"
)

type Error struct {
	Code  int    `json:"code" validate:"nonzero"`
	Error string `json:"error" validate:"nonzero"`
}

func (s Error) Validate() error {

	return validator.Validate(s)
}
