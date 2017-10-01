package node

import (
	"fmt"
	"gopkg.in/validator.v2"
	"strconv"
	"github.com/zero-os/0-orchestrator/api/tools"
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

func (s GWCreate) Validate(aysClient *tools.AYStool, repoName string) error {
	for _, proxy := range s.Httpproxies {
		if err := proxy.Validate(); err != nil {
			return err
		}
	}
	nicnames := make(map[string]struct{})
	for _, nic := range s.Nics {
		if err := nic.Validate(aysClient, repoName); err != nil {
			return err
		}
		// check if the first char is not number
		first_char := string(nic.Name[0])
		_, err := strconv.ParseInt(first_char, 10, 64)
		if err == nil {
			return fmt.Errorf("NIC name can not start with number")
		}

		if _, exists := nicnames[nic.Name]; exists {
			return fmt.Errorf("Duplicate nic names detected")
		}
		nicnames[nic.Name] = struct{}{}
	}
	for _, portforward := range s.Portforwards {
		if err := portforward.Validate(); err != nil {
			return err
		}
	}
	return validator.Validate(s)
}
