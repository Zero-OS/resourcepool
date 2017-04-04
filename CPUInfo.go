package main

import (
	"gopkg.in/validator.v2"
)

// Information about physical CPUs
type CPUInfo struct {
	CacheSize int      `json:"cacheSize" validate:"nonzero"`
	Cores     int      `json:"cores" validate:"nonzero"`
	Family    string   `json:"family" validate:"nonzero"`
	Flags     []string `json:"flags" validate:"nonzero"`
	Mhz       float64  `json:"mhz" validate:"nonzero"`
}

func (s CPUInfo) Validate() error {

	return validator.Validate(s)
}
