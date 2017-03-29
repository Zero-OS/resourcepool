package client

import (
	"gopkg.in/validator.v2"
)

type AysRepositoryRepository_nameBlueprintBlueprint_namePutReqBody struct {
	Content object `json:"content" validate:"nonzero"`
	Name    string `json:"name" validate:"nonzero"`
}

func (s AysRepositoryRepository_nameBlueprintBlueprint_namePutReqBody) Validate() error {

	return validator.Validate(s)
}
