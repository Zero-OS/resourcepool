package main

import (
	"gopkg.in/validator.v2"
)

type RunState struct {
}

func (s RunState) Validate() error {

	return validator.Validate(s)
}
