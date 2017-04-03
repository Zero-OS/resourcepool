package client

import (
	"encoding/json"
	"gopkg.in/validator.v2"
)

type AysRepositoryRepositoryBlueprintBlueprintPutReqBody struct {
	Content json.RawMessage `json:"content" validate:"nonzero"`
	Name    string          `json:"name" validate:"nonzero"`
}

func (s AysRepositoryRepositoryBlueprintBlueprintPutReqBody) Validate() error {

	return validator.Validate(s)
}
