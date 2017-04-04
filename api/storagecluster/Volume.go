package storagecluster

import (
	"gopkg.in/validator.v2"
)

type Volume struct {
	Blocksize int              `json:"blocksize" validate:"nonzero"`
	Deduped   bool             `json:"deduped" validate:"nonzero"`
	Driver    string           `json:"driver,omitempty"`
	Id        string           `json:"id" validate:"nonzero"`
	ReadOnly  bool             `json:"readOnly,omitempty"`
	Size      int              `json:"size" validate:"nonzero"`
	Status    EnumVolumeStatus `json:"status" validate:"nonzero"`
}

func (s Volume) Validate() error {

	return validator.Validate(s)
}
