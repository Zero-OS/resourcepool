package node

import (
	"gopkg.in/validator.v2"
)

// ContainerUpdate is a Struct for container update.
type ContainerUpdate struct {
	Nics []ContainerNIC `json:"nics"`
}

// Validate method to validate the nics passed for the update
func (s ContainerUpdate) Validate() error {
	for _, nic := range s.Nics {
		if err := nic.Validate(); err != nil {
			return err
		}
	}
	return validator.Validate(s)
}
