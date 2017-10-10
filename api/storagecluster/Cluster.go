package storagecluster

import (
	"gopkg.in/validator.v2"
)

type Cluster struct {
	StorageServers []StorageServer      `yaml:"storageServers" json:"storageServers" validate:"nonzero"`
	DriveType      EnumClusterDriveType `yaml:"driveType" json:"driveType" validate:"nonzero"`
	MetaDriveType  EnumClusterDriveType `yaml:"metaDriveType" json:"metaDriveType"`
	Label          string               `yaml:"label" json:"label" validate:"nonzero"`
	Nodes          []string             `yaml:"nodes" json:"nodes" validate:"nonzero"`
	Status         EnumClusterStatus    `yaml:"status" json:"status" validate:"nonzero"`
}

func (s Cluster) Validate() error {

	return validator.Validate(s)
}
