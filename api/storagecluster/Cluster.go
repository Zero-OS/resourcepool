package storagecluster

import (
	"gopkg.in/validator.v2"
)

type Cluster struct {
	DataStorage     []HAStorageServer    `yaml:"dataStorage" json:"dataStorage" validate:"nonzero"`
	DriveType       EnumClusterDriveType `yaml:"driveType" json:"driveType" validate:"nonzero"`
	Label           string               `yaml:"label" json:"label" validate:"nonzero"`
	MetadataStorage []HAStorageServer    `yaml:"metadataStorage" json:"metadataStorage" validate:"nonzero"`
	Nodes           []string             `yaml:"nodes" json:"nodes" validate:"nonzero"`
	Status          EnumClusterStatus    `yaml:"status" json:"status" validate:"nonzero"`
}

func (s Cluster) Validate() error {

	return validator.Validate(s)
}
