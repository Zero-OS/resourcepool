package node

import (
	"gopkg.in/validator.v2"
)

type ContainerNICConfig struct {
	Dhcp    bool     `json:"dhcp"`
	Cidr    string   `json:"cidr"`
	Gateway string   `json:"gateway"`
	DNS     []string `json:"dns"`
}

type ContainerNIC struct {
	Config ContainerNICConfig   `json:"config,omitempty" yaml:"config,omitempty"`
	Hwaddr string               `json:"hwaddr,omitempty" yaml:"hwaddr,omitempty"`
	Id     string               `json:"id" validate:"nonzero" yaml:"id" validate:"nonzero"`
	Type   EnumContainerNICType `json:"type" validate:"nonzero" yaml:"type" validate:"nonzero"`
}

func (s ContainerNIC) Validate() error {

	return validator.Validate(s)
}
