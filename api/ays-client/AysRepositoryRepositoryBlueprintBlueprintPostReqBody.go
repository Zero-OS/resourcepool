package client

import (
	"gopkg.in/validator.v2"
)

type AysRepositoryRepositoryBlueprintBlueprintPostReqBody struct {
	Message string `json:"message,omitempty"`
}

func (s AysRepositoryRepositoryBlueprintBlueprintPostReqBody) Validate() error {

	return validator.Validate(s)
}
