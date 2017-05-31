package node

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

// Arguments for a bridge.create job
type BridgeCreate struct {
	Hwaddr      string                      `json:"hwaddr,omitempty" validate:"macaddress=empty"`
	Name        string                      `json:"name" validate:"nonzero,servicename"`
	Nat         bool                        `json:"nat"`
	NetworkMode EnumBridgeCreateNetworkMode `json:"networkMode" validate:"nonzero"`
	Setting     BridgeCreateSetting         `json:"setting" validate:"nonzero"`
}

func (s BridgeCreate) Validate() error {
	networkModeEnums := map[interface{}]struct{}{
		EnumBridgeCreateNetworkModednsmasq: struct{}{},
		EnumBridgeCreateNetworkModenone:    struct{}{},
		EnumBridgeCreateNetworkModestatic:  struct{}{},
	}

	if err := validators.ValidateEnum("NetworkMode", s.NetworkMode, networkModeEnums); err != nil {
		return err
	}

	return validator.Validate(s)
}
