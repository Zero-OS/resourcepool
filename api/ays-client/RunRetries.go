package client

import (
	"gopkg.in/validator.v2"
)

type RunRetries struct {
	Duration         int   `json:"duration" validate:"nonzero"`
	RemainingRetries []int `json:"remaining-retries" validate:"nonzero"`
	RetryNumber      int   `json:"retry-number" validate:"nonzero"`
}

func (s RunRetries) Validate() error {

	return validator.Validate(s)
}
