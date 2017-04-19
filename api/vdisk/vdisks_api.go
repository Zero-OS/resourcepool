package vdisk

import (
	ays "github.com/g8os/grid/api/ays-client"
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
