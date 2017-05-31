package node

import (
	"gopkg.in/validator.v2"
	"github.com/zero-os/0-orchestrator/api/validators"
)

type PortForward struct {
	Dstip     string           `json:"dstip" validate:"nonzero"`
	Dstport   int              `json:"dstport" validate:"nonzero"`
	Protocols []EnumIPProtocol `json:"protocols" validate:"nonzero"`
	Srcip     string           `json:"srcip" validate:"nonzero"`
	Srcport   int              `json:"srcport" validate:"nonzero"`
}

func (s PortForward) Validate() error {
	protocolsEnums := map[interface{}]struct{}{
		EnumIPProtocoltcp: struct{}{},
		EnumIPProtocoludp:    struct{}{},
	}

	for _, protocol := range s.Protocols {
		if err := validators.ValidateEnum("Protocols", protocol, protocolsEnums); err != nil {
			return err
		}

	}
	return validator.Validate(s)
}
