package node

import (
	"fmt"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type NicInterface interface {
	ValidateServices(tools.AYStool, string) error
	Validate() error
}

type BaseNic struct {
	Id    string               `json:"id,omitempty" yaml:"id,omitempty"`
	Name  string               `json:"name,omitempty" yaml:"name,omitempty"`
	Type  EnumContainerNICType `json:"type" yaml:"type" validate:"nonzero"`
	Token string               `json:"token,omitempty" yaml:"token,omitempty"`
}

func (s BaseNic) Validate() error {
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

func (s BaseNic) ValidateServices(aysClient tools.AYStool, repoName string) error {
	if s.Type == EnumContainerNICTypebridge {
		exists, err := aysClient.ServiceExists("bridge", s.Id, repoName)
		if err != nil {
			return err
		}
		if !exists {
			return fmt.Errorf("Bridge %s does not exists", s.Id)
		}
	}
	return nil
}
