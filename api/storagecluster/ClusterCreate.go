package storagecluster

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type ClusterCreate struct {
	DriveType     EnumClusterCreateDriveType `yaml:"driveType" json:"driveType" validate:"nonzero"`
	MetaDriveType EnumClusterCreateDriveType `yaml:"metaDriveType" json:"metaDriveType"`
	Label         string                     `yaml:"label" json:"label" validate:"nonzero,servicename"`
	Nodes         []string                   `yaml:"nodes" json:"nodes" validate:"nonzero"`
	Servers       int                        `yaml:"servers" json:"servers" validate:"nonzero"`
	ClusterType   EnumClusterType            `yaml:"clusterType" json:"clusterType" validate:"nonzero"`
	K             int                        `yaml:"k" json:"k"`
	M             int                        `yaml:"m" json:"m"`
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

	if string(s.MetaDriveType) != "" {
		if err := validators.ValidateEnum("MetaDriveType", s.MetaDriveType, typeEnums); err != nil {
			return err
		}
	}

	clusterTypeEnums := map[interface{}]struct{}{
		EnumClusterTypeBlock:  struct{}{},
		EnumClusterTypeObject: struct{}{},
	}

	if err := validators.ValidateEnum("ClusterType", s.ClusterType, clusterTypeEnums); err != nil {
		return err
	}

	if err := validators.ValidateCluster(string(s.ClusterType), s.K, s.M, s.Servers, string(s.MetaDriveType)); err != nil {
		return err
	}

	return validator.Validate(s)
}
