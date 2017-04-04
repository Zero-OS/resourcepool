package main

import (
	"gopkg.in/validator.v2"
)

// Arguments for a bridge.create job
type BridgeCreate struct {
	Hwaddr      string                      `json:"hwaddr,omitempty"`
	Name        string                      `json:"name" validate:"nonzero"`
	Nat         bool                        `json:"nat" validate:"nonzero"`
	NetworkMode EnumBridgeCreateNetworkMode `json:"networkMode" validate:"nonzero"`
	Settings    BridgeCreateSetting         `json:"settings" validate:"nonzero"`
}

func (s BridgeCreate) Validate() error {

	return validator.Validate(s)
}
