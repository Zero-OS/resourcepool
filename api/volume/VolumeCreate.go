package volume

import (
	"gopkg.in/validator.v2"
)

type VolumeCreate struct {
	ID                 string                     `yaml:"-" json:"id" validate:"nonzero"`
	Blocksize          int                        `yaml:"blocksize" json:"blocksize" validate:"nonzero"`
	ReadOnly           bool                       `yaml:"readOnly" json:"readOnly,omitempty"`
	Size               int                        `yaml:"size" json:"size" validate:"nonzero"`
	Storagecluster     string                     `yaml:"storagecluster" json:"storagecluster" validate:"nonzero"`
	Templatevolume     string                     `yaml:"templatevolume" json:"templatevolume,omitempty"`
	TlogStoragecluster string                     `yaml:"tlogStoragecluster" json:"tlogStoragecluster,omitempty"`
	Volumetype         EnumVolumeCreateVolumetype `yaml:"volumetype" json:"volumetype" validate:"nonzero"`
}

func (s VolumeCreate) Validate() error {

	return validator.Validate(s)
}
