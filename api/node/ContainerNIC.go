package node

import (
	"github.com/zero-os/0-orchestrator/api/tools"
	validator "gopkg.in/validator.v2"
)

type ContainerNICConfig struct {
	Dhcp    bool     `json:"dhcp"`
	Cidr    string   `json:"cidr"`
	Gateway string   `json:"gateway"`
	DNS     []string `json:"dns"`
}

type ContainerNIC struct {
	BaseNic `yaml:",inline"`
	Config  ContainerNICConfig `json:"config,omitempty" yaml:"config,omitempty"`
	Hwaddr  string             `json:"hwaddr,omitempty" yaml:"hwaddr,omitempty" validate:"macaddress=empty"`
}

func (s ContainerNIC) Validate(aysClient *tools.AYStool, repoName string) error {
	if err := s.BaseNic.Validate(aysClient, repoName); err != nil {
		return err
	}

	return validator.Validate(s)
}

func (s ContainerNICConfig) Validate() error {
	return validator.Validate(s)
}
