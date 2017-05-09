package storagecluster

import (
	"github.com/g8os/resourcepool/api/validators"
	"gopkg.in/validator.v2"
)

type ClusterCreate struct {
	DriveType EnumClusterCreateDriveType `yaml:"driveType" json:"driveType" validate:"nonzero"`
	Label     string                     `yaml:"label" json:"label" validate:"nonzero,servicename"`
	Nodes     []string                   `yaml:"nodes" json:"nodes" validate:"nonzero"`
	Servers   int                        `yaml:"servers" json:"servers" validate:"nonzero"`
}

func (s ClusterCreate) Validate() error {
	typeEnums := map[interface{}]struct{}{
		EnumClusterCreateDriveTypenvme:    struct{}{},
		EnumClusterCreateDriveTypessd:     struct{}{},
		EnumClusterCreateDriveTypehdd:     struct{}{},
		EnumClusterCreateDriveTypearchive: struct{}{},
	}

	if err := validators.ValidateEnum("DriveType", s.DriveType, typeEnums); err != nil {
		return err
	}

	return validator.Validate(s)
}
