package storagecluster

import (
	"gopkg.in/validator.v2"
)

type ClusterCreate struct {
	DriveType     EnumClusterCreateDriveType `json:"driveType" validate:"nonzero"`
	Label         string                     `json:"label" validate:"nonzero"`
	NumberOfNodes int                        `json:"numberOfNodes" validate:"nonzero"`
	SlaveNodes    bool                       `json:"slaveNodes" validate:"nonzero"`
}

func (s ClusterCreate) Validate() error {

	return validator.Validate(s)
}
