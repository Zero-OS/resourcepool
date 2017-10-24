package storagecluster

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

type ClusterCreate struct {
	DriveType            EnumClusterCreateDriveType `yaml:"driveType" json:"driveType" validate:"nonzero"`
	MetaDriveType        EnumClusterCreateDriveType `yaml:"metaDriveType" json:"metaDriveType"`
	ServersPerMetaDrive  int                        `yaml:"serversPerMetaDrive" json:"serversPerMetaDrive"`
	Label                string                     `yaml:"label" json:"label" validate:"nonzero,servicename"`
	Nodes                []string                   `yaml:"nodes" json:"nodes" validate:"nonzero"`
	Servers              int                        `yaml:"servers" json:"servers" validate:"nonzero"`
	ClusterType          EnumClusterType            `yaml:"clusterType" json:"clusterType" validate:"nonzero"`
	DataShards           int                        `yaml:"dataShards" json:"dataShards"`
	ParityShards         int                        `yaml:"parityShards" json:"parityShards"`
	ZerostorOrganization string                     `yaml:"zerostorOrganization" json:"zerostorOrganization"`
	ZerostorNamespace    string                     `yaml:"zerostorNamespace" json:"zerostorNamespace"`
	ZerostorClientID     string                     `yaml:"zerostorClientID" json:"zerostorClientID"`
	ZerostorSecret       string                     `yaml:"zerostorSecret" json:"zerostorSecret"`
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

	clusterTypeEnums := map[interface{}]struct{}{
		EnumClusterTypeBlock:  struct{}{},
		EnumClusterTypeObject: struct{}{},
	}

	if err := validators.ValidateEnum("ClusterType", s.ClusterType, clusterTypeEnums); err != nil {
		return err
	}

	if s.ClusterType == EnumClusterTypeObject {
		if err := validators.ValidateEnum("MetaDriveType", s.MetaDriveType, typeEnums); err != nil {
			return err
		}

		if err := validators.ValidateObjectCluster(s.DataShards, s.ParityShards, s.Servers, string(s.MetaDriveType), s.ServersPerMetaDrive, s.ZerostorOrganization, s.ZerostorNamespace, s.ZerostorClientID, s.ZerostorSecret); err != nil {
			return err
		}
	}

	return validator.Validate(s)
}
