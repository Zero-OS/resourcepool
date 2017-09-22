package node

import (
	"gopkg.in/validator.v2"
)

type SnapShotCreate struct {
	Name string `yaml:"name" json:"name" validate:"servicename,max=50"`
}

func (s SnapShotCreate) Validate() error {

	return validator.Validate(s)
}
