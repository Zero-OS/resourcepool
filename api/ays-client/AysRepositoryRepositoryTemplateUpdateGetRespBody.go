package client

import (
	"gopkg.in/validator.v2"
)

type AysRepositoryRepositoryTemplateUpdateGetRespBody struct {
	Message string `json:"message" validate:"nonzero"`
}

func (s AysRepositoryRepositoryTemplateUpdateGetRespBody) Validate() error {

	return validator.Validate(s)
}
