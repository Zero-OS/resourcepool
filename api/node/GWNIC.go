package node

import (
	"fmt"
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
	Config         *GWNICConfig    `json:"config,omitempty" yaml:"config,omitempty"`
	Dhcpserver     *DHCP           `json:"dhcpserver,omitempty" yaml:"dhcpserver,omitempty"`
	Id             string          `json:"id,omitempty"   yaml:"id,omitempty"`
	Name           string          `json:"name" yaml:"name" validate:"nonzero"`
	Type           EnumGWNICType   `json:"type" yaml:"type" validate:"nonzero"`
	ZerotierBridge *ZerotierBridge `json:"zerotierbridge,omitempty" yaml:"zerotierbridge,omitempty"`
	Token          string          `json:"token,omitempty" yaml:"token,omitempty"`
}

func (s GWNIC) Validate() error {
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
		EnumGWNICTypezerotier: struct{}{},
		EnumGWNICTypevxlan:    struct{}{},
		EnumGWNICTypevlan:     struct{}{},
		EnumGWNICTypedefault:  struct{}{},
		EnumGWNICTypebridge:   struct{}{},
	}

	if err := validators.ValidateEnum("Type", s.Type, nicTypes); err != nil {
		return err
	}

	if err := validators.ValidateConditional(s.Type, EnumGWNICTypedefault, s.Id, "Id"); err != nil {
		return err
	}

	if s.Type != EnumGWNICTypezerotier && s.Token != "" {
		return fmt.Errorf("Token: set for a nic that is not of type zerotier.")
	}

	return validator.Validate(s)
}
