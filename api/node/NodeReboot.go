package node

import "gopkg.in/validator.v2"

type NodeReboot struct {
	Force bool `json:"force"`
}

func (s NodeReboot) Validate() error {

	return validator.Validate(s)
}
