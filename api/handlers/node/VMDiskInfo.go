package node

import (
	"gopkg.in/validator.v2"
)

type VMDiskInfo struct {
	ReadIops        uint64 `json:"readIops" validate:"nonzero"`
	ReadThroughput  uint64 `json:"readThroughput" validate:"nonzero"`
	WriteIops       uint64 `json:"writeIops" validate:"nonzero"`
	WriteThroughput uint64 `json:"writeThroughput" validate:"nonzero"`
}

func (s VMDiskInfo) Validate() error {

	return validator.Validate(s)
}
