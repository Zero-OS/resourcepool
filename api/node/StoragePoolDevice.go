package node

import (
	"gopkg.in/validator.v2"
)

type StoragePoolDevice struct {
	DeviceName string                      `json:"deviceName" validate:"nonzero"`
	Status     EnumStoragePoolDeviceStatus `json:"status" validate:"nonzero"`
	UUID       string                      `json:"uuid" validate:"nonzero"`
}

func (s StoragePoolDevice) Validate() error {

	return validator.Validate(s)
}
