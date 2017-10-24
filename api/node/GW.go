package node

import (
	"github.com/zero-os/0-orchestrator/api/tools"
	"gopkg.in/validator.v2"
)

type GetGW struct {
	Domain         string            `json:"domain" validate:"nonzero"`
	Httpproxies    []HTTPProxy       `json:"httpproxies,omitempty"`
	Nics           []GWNIC           `json:"nics" validate:"nonzero"`
	Portforwards   []PortForward     `json:"portforwards,omitempty"`
	ZerotierNodeId string            `json:"zerotiernodeid,omitempty"`
	Status         EnumGatewayStatus `json:"status" validate:"nonzero"`
}

type MigrateGW struct {
	Node string `json:"node" yaml:"node" validate:"nonzero"`
}

func (s MigrateGW) Validate() error {
	return validator.Validate(s)
}

type GW struct {
	Domain       string        `json:"domain" yaml:"domain" validate:"nonzero"`
	Httpproxies  []HTTPProxy   `json:"httpproxies,omitempty" yaml:"httpproxies"`
	Nics         []GWNIC       `json:"nics" yaml:"nics" validate:"nonzero"`
	Portforwards []PortForward `json:"portforwards,omitempty" yaml:"portforwards,omitempty"`
}

func (s GW) Validate(aysClient *tools.AYStool, repoName string) error {
	for _, proxy := range s.Httpproxies {
		if err := proxy.Validate(); err != nil {
			return err
		}
	}
	for _, nic := range s.Nics {
		if err := nic.Validate(aysClient, repoName); err != nil {
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
