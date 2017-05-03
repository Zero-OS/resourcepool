package storagecluster

import (
	"gopkg.in/validator.v2"
)

type ClusterCreate struct {
	DriveType  EnumClusterCreateDriveType `yaml:"driveType" json:"driveType" validate:"nonzero"`
	Label      string                     `yaml:"label" json:"label" validate:"nonzero,servicename"`
	Nodes      []string                   `yaml:"nodes" json:"nodes" validate:"nonzero"`
	Servers    int                        `yaml:"servers" json:"servers" validate:"nonzero"`
	SlaveNodes bool                       `yaml:"slaveNodes" json:"slaveNodes"`
}

func (s ClusterCreate) Validate() error {

	return validator.Validate(s)
}
