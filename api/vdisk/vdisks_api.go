package vdisk

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// VdisksAPI is API implementation of /vdisks root endpoint
type VdisksAPI struct {
	AysRepo string
	AysAPI  *ays.AtYourServiceAPI
}

func NewVdiskAPI(repo string, client *ays.AtYourServiceAPI) VdisksAPI {
	return VdisksAPI{
		AysRepo: repo,
		AysAPI:  client,
	}
}
