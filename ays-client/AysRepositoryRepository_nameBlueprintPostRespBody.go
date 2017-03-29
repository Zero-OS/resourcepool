package client

import (
	"gopkg.in/validator.v2"
)

type AysRepositoryRepository_nameBlueprintPostRespBody struct {
	Content object `json:"content" validate:"nonzero"`
	Name    string `json:"name" validate:"nonzero"`
}

func (s AysRepositoryRepository_nameBlueprintPostRespBody) Validate() error {

	return validator.Validate(s)
}
