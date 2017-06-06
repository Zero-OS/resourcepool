package node

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type GWNIC struct {
	Config         *GWNICConfig  `json:"config,omitempty" yaml:"config,omitempty"`
	Dhcpserver     *DHCP         `json:"dhcpserver,omitempty" yaml:"dhcpserver,omitempty"`
	Id             string        `json:"id,omitempty"   yaml:"id,omitempty"`
	Name           string        `json:"name" yaml:"name" validate:"nonzero"`
	Type           EnumGWNICType `json:"type" yaml:"type" validate:"nonzero"`
	ZerotierBridge string        `json:"zerotierbridge" yaml:"zerotierbridge"`
}

func (s GWNIC) Validate() error {
	if s.Config != nil {
		if err := s.Config.Validate(); err != nil {
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

	return validator.Validate(s)
}
