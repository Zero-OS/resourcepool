package node

import (
	"gopkg.in/validator.v2"
)

type DHCP struct {
	Hosts       []GWHost `json:"hosts" yaml:"hosts" validate:"nonzero"`
	Nameservers []string `json:"nameservers,omitempty" yaml:"nameservers,omitempty"`
}

func (s DHCP) Validate() error {
	for _, host := range s.Hosts {
		if err := host.Validate(); err != nil {
			return err
		}
	}
	return validator.Validate(s)
}
