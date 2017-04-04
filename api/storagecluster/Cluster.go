package storagecluster

import (
	"gopkg.in/validator.v2"
)

type Cluster struct {
	DataStorage     []StorageServer      `json:"dataStorage" validate:"nonzero"`
	DriveType       EnumClusterDriveType `json:"driveType" validate:"nonzero"`
	Label           string               `json:"label" validate:"nonzero"`
	MetadataStorage []StorageServer      `json:"metadataStorage" validate:"nonzero"`
	SlaveNodes      bool                 `json:"slaveNodes" validate:"nonzero"`
	Status          EnumClusterStatus    `json:"status" validate:"nonzero"`
}

func (s Cluster) Validate() error {

	return validator.Validate(s)
}
