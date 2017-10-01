package node

import (
	"gopkg.in/validator.v2"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ContainerUpdate is a Struct for container update.
type ContainerUpdate struct {
	Nics []ContainerNIC `json:"nics"`
}

// Validate method to validate the nics passed for the update
func (s ContainerUpdate) Validate(aysClient *tools.AYStool, repoName string) error {
	for _, nic := range s.Nics {
		if err := nic.Validate(aysClient, repoName); err != nil {
			return err
		}
	}
	return validator.Validate(s)
}
