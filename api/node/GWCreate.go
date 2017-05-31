package node

import (
	"gopkg.in/validator.v2"
)

type GWCreate struct {
	Name         string        `json:"name" yaml:"name"  validate:"nonzero"`
	Domain       string        `json:"domain" yaml:"domain"  validate:"nonzero"`
	Httpproxies  []HTTPProxy   `json:"httpproxies" yaml:"httpproxies"`
	Nics         []GWNIC       `json:"nics" yaml:"nics" validate:"nonzero"`
	Portforwards []PortForward `json:"portforwards,omitempty" yaml:"portforwards,omitempty"`
}

func (s GWCreate) Validate() error {
	for _, proxy := range s.Httpproxies {
		if err := proxy.Validate(); err != nil {
			return err
		}
	}
	for _, nic := range s.Nics {
		if err := nic.Validate(); err != nil {
			return err
		}
	}
	for _, portforward := range s.Portforwards {
		if err := portforward.Validate(); err != nil {
			return err
		}
	}
	return validator.Validate(s)
}
