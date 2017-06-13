package node

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
	"fmt"
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
	Name   string               `json:"name,omitempty" yaml:"name,omitempty"`
	Type   EnumContainerNICType `json:"type" yaml:"type" validate:"nonzero"`
	Token  string               `json:"token,omitempty" yaml:"token,omitempty"`
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

	if s.Type != EnumContainerNICTypezerotier && s.Token != "" {
		return fmt.Errorf("Token: set for a nic that is not of type zerotier.")
	}

	return validator.Validate(s)
}
