package node

import (
	"gopkg.in/validator.v2"
)

type VMNetInfo struct {
	ReceivedPackets       uint64 `json:"receivedPackets" validate:"nonzero"`
	ReceivedThroughput    uint64 `json:"receivedThroughput" validate:"nonzero"`
	TransmittedPackets    uint64 `json:"transmittedPackets" validate:"nonzero"`
	TransmittedThroughput uint64 `json:"transmittedThroughput" validate:"nonzero"`
}

func (s VMNetInfo) Validate() error {

	return validator.Validate(s)
}
