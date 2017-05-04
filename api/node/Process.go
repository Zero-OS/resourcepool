package node

import (
	"gopkg.in/validator.v2"
)

type Process struct {
	Cmdline string   `json:"cmdline" validate:"nonzero"`
	Cpu     CPUStats `json:"cpu" validate:"nonzero"`
	Pid     uint64   `json:"pid" validate:"nonzero"`
	Rss     uint64   `json:"rss" validate:"nonzero"`
	Swap    uint64   `json:"swap" validate:"nonzero"`
	Vms     uint64   `json:"vms" validate:"nonzero"`
}

func (s Process) Validate() error {

	return validator.Validate(s)
}
