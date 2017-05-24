package node

import (
	"github.com/g8os/resourcepool/api/validators"
	"gopkg.in/validator.v2"
)

type GWHost struct {
	Cloudinit  *CloudInit `json:"cloudinit,omitempty" yaml:"cloudinit,omitempty"`
	Ip6address string     `json:"ip6address,omitempty" yaml:"ip6address,omitempty"`
	Hostname   string     `json:"hostname"  yaml:"hostname" validate:"nonzero"`
	Ipaddress  string     `json:"ipaddress" yaml:"ipaddress" validate:"nonzero"`
	Macaddress string     `json:"macaddress" yaml:"macaddress" validate:"nonzero,macaddress"`
}

func (s GWHost) Validate() error {
	if s.Cloudinit != nil {
		if err := s.Cloudinit.Validate(); err != nil {
			return err
		}
	}
	if err := validators.ValidateIp4(s.Ipaddress); err != nil {
		return err
	}
	if s.Ip6address != "" {
		if err := validators.ValidateIp6(s.Ip6address); err != nil {
			return err
		}
	}
	return validator.Validate(s)
}
