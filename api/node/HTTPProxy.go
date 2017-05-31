package node

import (
	"gopkg.in/validator.v2"
	"github.com/zero-os/0-orchestrator/api/validators"
)

type HTTPProxy struct {
	Destinations []string       `json:"destinations" validate:"nonzero"`
	Host         string         `json:"host" validate:"nonzero"`
	Types        []EnumHTTPType `json:"types" validate:"nonzero"`
}

func (s HTTPProxy) Validate() error {

	httpTypes := map[interface{}]struct{}{
		EnumHTTPTypehttp: struct{}{},
		EnumHTTPTypehttps:    struct{}{},
	}

	for _, httpType := range s.Types {
		if err := validators.ValidateEnum("Types", httpType, httpTypes); err != nil {
			return err
		}

	}
	return validator.Validate(s)
}
