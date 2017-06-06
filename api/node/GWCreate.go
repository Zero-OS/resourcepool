package node

import (
	"gopkg.in/validator.v2"
)

type ListGW struct {
	Name           string        `json:"name" validate:"nonzero"`
	Domain         string        `json:"domain" validate:"nonzero"`
	Httpproxies    []HTTPProxy   `json:"httpproxies,omitempty"`
	Nics           []GWNIC       `json:"nics" validate:"nonzero"`
	Portforwards   []PortForward `json:"portforwards,omitempty"`
	ZerotierNodeId string        `json:"zerotiernodeid,omitempty"`
}

type GWCreate struct {
	Name         string        `json:"name" yaml:"name"  validate:"nonzero"`
	Domain       string        `json:"domain" yaml:"domain"  validate:"nonzero"`
	Httpproxies  []HTTPProxy   `json:"httpproxies,omitempty" yaml:"httpproxies,omitempty"`
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
