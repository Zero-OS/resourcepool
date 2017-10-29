package webhook

import (
	"github.com/zero-os/0-orchestrator/api/validators"
	"gopkg.in/validator.v2"
)

// A webhook
type Webhook struct {
	EventTypes []EnumEventType `json:"eventtypes" validate:"nonzero"`
	Name       string          `json:"name" validate:"nonzero"`
	Url        string          `json:"url" validate:"nonzero"`
}

func (s Webhook) Validate() error {

	eventTypes := map[interface{}]struct{}{
		EnumEventTypeOrk: struct{}{},
	}

	for _, eventType := range s.EventTypes {
		if err := validators.ValidateEnum("EventTypes", eventType, eventTypes); err != nil {
			return err
		}

	}

	return validator.Validate(s)
}
