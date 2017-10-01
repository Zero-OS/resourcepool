package node

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
	"github.com/zero-os/0-orchestrator/api/tools"
	"fmt"
)

// Definition of a virtual nic
type NicLink struct {
	Id         string          `json:"id"`
	Macaddress string          `json:"macaddress" validate:"macaddress=empty"`
	Type       EnumNicLinkType `json:"type" validate:"nonzero"`
}

func (s NicLink) Validate(aysClient *tools.AYStool, repoName string) error {
	typeEnums := map[interface{}]struct{}{
		EnumNicLinkTypevlan:    struct{}{},
		EnumNicLinkTypevxlan:   struct{}{},
		EnumNicLinkTypedefault: struct{}{},
		EnumNicLinkTypebridge:  struct{}{},
	}

	if err := validators.ValidateEnum("Type", s.Type, typeEnums); err != nil {
		return err
	}

	if err := validators.ValidateConditional(s.Type, EnumNicLinkTypedefault, s.Id, "Id"); err != nil {
		return err
	}

	if s.Type == EnumNicLinkTypebridge {
		exists, err := aysClient.ServiceExists("bridge", s.Id, repoName)
		if err != nil {
			return err
		}
		if !exists {
			return fmt.Errorf("bridge %s does not exists", s.Id)
		}
	}

	return validator.Validate(s)
}
