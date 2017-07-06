package vdisk

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// VdisksAPI is API implementation of /vdisks root endpoint
type VdisksAPI struct {
	AysRepo string
	AysUrl  string
}

func NewVdiskAPI(repo string, aysurl string) VdisksAPI {
	return VdisksAPI{
		AysRepo: repo,
		AysUrl:  aysurl,
	}
}

func (api VdisksAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api VdisksAPI) AysRepoName() string {
	return api.AysRepo
}
