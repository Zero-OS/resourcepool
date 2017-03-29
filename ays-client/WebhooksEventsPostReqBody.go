package client

import (
	"gopkg.in/validator.v2"
)

type WebhooksEventsPostReqBody struct {
	Command string   `json:"command" validate:"nonzero"`
	Payload object   `json:"payload" validate:"nonzero"`
	Tags    []string `json:"tags" validate:"nonzero"`
}

func (s WebhooksEventsPostReqBody) Validate() error {

	return validator.Validate(s)
}
