package vdisk

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type VdiskCreate struct {
	ID        string                   `json:"id" validate:"nonzero"`
	Blocksize int                      `json:"blocksize" validate:"nonzero"`
	ImageID  string                   `json:"imageId,omitempty"`
	ReadOnly  bool                     `json:"readOnly,omitempty"`
	Size      int                      `json:"size" validate:"nonzero"`
	Vdisktype EnumVdiskCreateVdisktype `json:"type" validate:"nonzero"`
}

func (s VdiskCreate) Validate() error {
	typeEnums := map[interface{}]struct{}{
		EnumVdiskCreateVdisktypeboot:  struct{}{},
		EnumVdiskCreateVdisktypedb:    struct{}{},
		EnumVdiskCreateVdisktypecache: struct{}{},
		EnumVdiskCreateVdisktypetmp:   struct{}{},
	}

	if err := validators.ValidateEnum("Vdisktype", s.Vdisktype, typeEnums); err != nil {
		return err
	}

	// TODO: validate image ID
	// if err := validators.ValidateVdisk(string(s.Vdisktype), s.Templatevdisk, s.Blocksize); err != nil {
	// 	return err
	// }

	return validator.Validate(s)
}
