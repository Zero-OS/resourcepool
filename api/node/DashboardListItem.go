package node

import (
	"gopkg.in/validator.v2"
)

type DashboardListItem struct {
	Slug      string `json:"slug" validate:"nonzero"`
	Dashboard string `json:"dashboard" validate:"nonzero"`
	Name      string `json:"name" validate:"nonzero"`
	Url       string `json:"url"`
}

func (s DashboardListItem) Validate() error {

	return validator.Validate(s)
}
