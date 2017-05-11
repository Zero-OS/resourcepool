package node

import (
	"github.com/g8os/resourcepool/api/validators"
	"gopkg.in/validator.v2"
)

// Definition of a virtual nic
type NicLink struct {
	Id         string          `json:"id"`
	Macaddress string          `json:"macaddress" validate:"macaddress=empty"`
	Type       EnumNicLinkType `json:"type" validate:"nonzero"`
}

func (s NicLink) Validate() error {
	typeEnums := map[interface{}]struct{}{
		EnumNicLinkTypevlan:    struct{}{},
		EnumNicLinkTypevxlan:   struct{}{},
		EnumNicLinkTypedefault: struct{}{},
	}

	if err := validators.ValidateEnum("Type", s.Type, typeEnums); err != nil {
		return err
	}

	if err := validators.ValidateConditional(s.Type, EnumNicLinkTypedefault, s.Id, "Id"); err != nil {
		return err
	}

	return validator.Validate(s)
}
