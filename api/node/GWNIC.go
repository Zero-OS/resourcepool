package node

import (
	"fmt"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type ZerotierBridge struct {
	Id    string `json:"id"   yaml:"id" validate:"nonzero"`
	Token string `json:"token,omitempty" yaml:"token,omitempty"`
}

func (s ZerotierBridge) Validate() error {
	return validator.Validate(s)
}

type GWNIC struct {
	BaseNic        `yaml:",inline"`
	Config         *GWNICConfig    `json:"config,omitempty" yaml:"config,omitempty"`
	Dhcpserver     *DHCP           `json:"dhcpserver,omitempty" yaml:"dhcpserver,omitempty"`
	ZerotierBridge *ZerotierBridge `json:"zerotierbridge,omitempty" yaml:"zerotierbridge,omitempty"`
}

func (s GWNIC) Validate(aysClient *tools.AYStool, repoName string) error {
	if err := s.BaseNic.Validate(aysClient, repoName); err != nil {
		return err
	}
	if s.Config != nil {
		if err := s.Config.Validate(); err != nil {
			return err
		}
	}

	if s.ZerotierBridge != nil {
		if err := s.ZerotierBridge.Validate(); err != nil {
			return err
		}
	}

	if s.Dhcpserver != nil && s.Dhcpserver.Hosts != nil {
		if err := s.Dhcpserver.Validate(); err != nil {
			return err
		}
		for _, host := range s.Dhcpserver.Hosts {
			if err := validators.ValidateIpInRange(s.Config.Cidr, host.Ipaddress); err != nil {
				return err
			}
		}
	}

	nicTypes := map[interface{}]struct{}{
		EnumContainerNICTypezerotier: struct{}{},
		EnumContainerNICTypevlan:     struct{}{},
		EnumContainerNICTypevxlan:    struct{}{},
		EnumContainerNICTypedefault:  struct{}{},
		EnumContainerNICTypebridge:   struct{}{},
	}

	if err := validators.ValidateEnum("Type", s.Type, nicTypes); err != nil {
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
