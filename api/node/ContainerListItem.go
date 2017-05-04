package node

import (
	"gopkg.in/validator.v2"
)

type ContainerListItem struct {
	Flist    string                      `json:"flist" validate:"nonzero"`
	Hostname string                      `json:"hostname" validate:"nonzero"`
	Name     string                      `json:"name" validate:"nonzero"`
	Status   EnumContainerListItemStatus `json:"status" validate:"nonzero"`
}

func (s ContainerListItem) Validate() error {

	return validator.Validate(s)
}
