package node

import (
	"fmt"

	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

// Arguments for a bridge.create job
type BridgeCreate struct {
	Hwaddr      string                      `json:"hwaddr,omitempty" validate:"macaddress=empty"`
	Name        string                      `json:"name" validate:"nonzero,servicename,max=15"`
	Nat         bool                        `json:"nat"`
	NetworkMode EnumBridgeCreateNetworkMode `json:"networkMode" validate:"nonzero"`
	Setting     BridgeCreateSetting         `json:"setting" validate:"nonzero"`
}

func (s BridgeCreate) Validate() error {
	if s.Name == "default" {
		return fmt.Errorf("Name: %v is not a valid value", s.Name)
	}
	networkModeEnums := map[interface{}]struct{}{
		EnumBridgeCreateNetworkModednsmasq: struct{}{},
		EnumBridgeCreateNetworkModenone:    struct{}{},
		EnumBridgeCreateNetworkModestatic:  struct{}{},
	}

	if err := validators.ValidateEnum("NetworkMode", s.NetworkMode, networkModeEnums); err != nil {
		return err
	}

	if (s.NetworkMode == EnumBridgeCreateNetworkModestatic || s.NetworkMode == EnumBridgeCreateNetworkModednsmasq) && s.Setting.Cidr == "" {
		return fmt.Errorf("Settings.Cidr: zero value")
	}

	if s.NetworkMode == EnumBridgeCreateNetworkModednsmasq {
		if s.Setting.Start == "" {
			return fmt.Errorf("Settings.Start: zero value")
		}
		if s.Setting.End == "" {
			return fmt.Errorf("Settings.End: zero value")
		}
	}

	return validator.Validate(s)
}
