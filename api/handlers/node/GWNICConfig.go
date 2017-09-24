package node

import (
	"gopkg.in/validator.v2"
)

type GWNICConfig struct {
	Cidr    string `json:"cidr" yaml:"cidr" validate:"nonzero,cidr"`
	Gateway string `json:"gateway,omitempty" yaml:"gateway,omitempty"`
}

func (s GWNICConfig) Validate() error {
	return validator.Validate(s)
}
