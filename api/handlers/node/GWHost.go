package node

import (
	"gopkg.in/validator.v2"
)

type GWHost struct {
	Cloudinit  *CloudInit `json:"cloudinit,omitempty" yaml:"cloudinit,omitempty"`
	Ip6address string     `json:"ip6address,omitempty" yaml:"ip6address,omitempty" validate:"ipv6=empty"`
	Hostname   string     `json:"hostname"  yaml:"hostname" validate:"nonzero"`
	Ipaddress  string     `json:"ipaddress" yaml:"ipaddress" validate:"nonzero,ipv4"`
	Macaddress string     `json:"macaddress" yaml:"macaddress" validate:"nonzero,macaddress"`
}

func (s GWHost) Validate() error {
	if s.Cloudinit != nil {
		if err := s.Cloudinit.Validate(); err != nil {
			return err
		}
	}

	return validator.Validate(s)
}
