package node

import (
	"gopkg.in/validator.v2"
	"github.com/g8os/grid/api/validators"
)

// Definition of a virtual nic
type NicLink struct {
	Id         string          `json:"id" validate:"nonzero"`
	Macaddress string          `json:"macaddress" validate:"nonzero,macaddress"`
	Type       EnumNicLinkType `json:"type" validate:"nonzero"`
}

func (s NicLink) Validate() error {
	typeEnums := map[interface{}]struct{}{
		EnumNicLinkTypevlan: struct{}{},
		EnumNicLinkTypevxlan:    struct{}{},
		EnumNicLinkTypedefault: struct {}{},
	}

	if err := validators.ValidateEnum("Type", s.Type, typeEnums); err != nil {
		return err
	}

	return validator.Validate(s)
}
