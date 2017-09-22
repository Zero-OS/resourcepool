package node

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

// Arguments to create a new storage pools
type StoragePoolCreate struct {
	DataProfile     EnumStoragePoolCreateDataProfile     `json:"dataProfile" validate:"nonzero"`
	Devices         []string                             `json:"devices" validate:"nonzero"`
	MetadataProfile EnumStoragePoolCreateMetadataProfile `json:"metadataProfile" validate:"nonzero"`
	Name            string                               `json:"name" validate:"nonzero,servicename"`
}

func (s StoragePoolCreate) Validate() error {
	dataEnums := map[interface{}]struct{}{
		EnumStoragePoolCreateDataProfileraid0:  struct{}{},
		EnumStoragePoolCreateDataProfileraid1:  struct{}{},
		EnumStoragePoolCreateDataProfileraid5:  struct{}{},
		EnumStoragePoolCreateDataProfileraid6:  struct{}{},
		EnumStoragePoolCreateDataProfileraid10: struct{}{},
		EnumStoragePoolCreateDataProfiledup:    struct{}{},
		EnumStoragePoolCreateDataProfilesingle: struct{}{},
	}

	if err := validators.ValidateEnum("DataProfile", s.DataProfile, dataEnums); err != nil {
		return err
	}

	metadataEnums := map[interface{}]struct{}{
		EnumStoragePoolCreateMetadataProfileraid0:  struct{}{},
		EnumStoragePoolCreateMetadataProfileraid1:  struct{}{},
		EnumStoragePoolCreateMetadataProfileraid5:  struct{}{},
		EnumStoragePoolCreateMetadataProfileraid6:  struct{}{},
		EnumStoragePoolCreateMetadataProfileraid10: struct{}{},
		EnumStoragePoolCreateMetadataProfiledup:    struct{}{},
		EnumStoragePoolCreateMetadataProfilesingle: struct{}{},
	}

	if err := validators.ValidateEnum("MetadataProfile", s.MetadataProfile, metadataEnums); err != nil {
		return err
	}

	return validator.Validate(s)
}
