package node

import (
	"gopkg.in/validator.v2"
)

type NodeMount struct {
	MountPoint string `json:"mountpoint" validate:"nonzero"`
	Device     string `json:"device" validate:"nonzero"`
	Opts       string `json:"opts" validate:"nonzero"`
	FsType     string `json:"fstype" validate:"nonzero"`
}

func (s NodeMount) Validate() error {

	return validator.Validate(s)
}
