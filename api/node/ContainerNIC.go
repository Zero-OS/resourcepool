package node

import (
	"gopkg.in/validator.v2"
	"github.com/g8os/resourcepool/api/validators"
)

type ContainerNICConfig struct {
	Dhcp    bool     `json:"dhcp"`
	Cidr    string   `json:"cidr"`
	Gateway string   `json:"gateway"`
	DNS     []string `json:"dns"`
}

type ContainerNIC struct {
	Config ContainerNICConfig   `json:"config,omitempty" yaml:"config,omitempty"`
	Hwaddr string               `json:"hwaddr,omitempty" yaml:"hwaddr,omitempty" validate:"macaddress=empty"`
	Id     string               `json:"id" yaml:"id" validate:"nonzero"`
	Type   EnumContainerNICType `json:"type" yaml:"type" validate:"nonzero"`
}

func (s ContainerNIC) Validate() error {
	typeEnums := map[interface{}]struct{}{
		EnumContainerNICTypezerotier: struct{}{},
		EnumContainerNICTypevxlan:    struct{}{},
		EnumContainerNICTypevlan:  struct{}{},
		EnumContainerNICTypedefault: struct {}{},
	}

	if err := validators.ValidateEnum("Type", s.Type, typeEnums); err != nil {
		return err
	}

	return validator.Validate(s)
}
