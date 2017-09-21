package client

import (
	"gopkg.in/validator.v2"
)

type AysRepositoryPostReqBody struct {
	Git_url string `json:"git_url" validate:"nonzero"`
	Name    string `json:"name" validate:"nonzero"`
}

func (s AysRepositoryPostReqBody) Validate() error {

	return validator.Validate(s)
}
