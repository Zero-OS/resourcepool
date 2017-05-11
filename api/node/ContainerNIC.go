package node

import (
	"github.com/g8os/resourcepool/api/validators"
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
	Hwaddr string               `json:"hwaddr,omitempty" yaml:"hwaddr,omitempty" validate:"macaddress=empty"`
	Id     string               `json:"id,omitempty" yaml:"id,omitempty"`
	Type   EnumContainerNICType `json:"type" yaml:"type" validate:"nonzero"`
}

func (s ContainerNIC) Validate() error {
	typeEnums := map[interface{}]struct{}{
		EnumContainerNICTypezerotier: struct{}{},
		EnumContainerNICTypevxlan:    struct{}{},
		EnumContainerNICTypevlan:     struct{}{},
		EnumContainerNICTypedefault:  struct{}{},
		EnumContainerNICTypebridge:   struct{}{},
	}

	if err := validators.ValidateEnum("Type", s.Type, typeEnums); err != nil {
		return err
	}

	if err := validators.ValidateConditional(s.Type, EnumContainerNICTypedefault, s.Id, "Id"); err != nil {
		return err
	}

	return validator.Validate(s)
}
