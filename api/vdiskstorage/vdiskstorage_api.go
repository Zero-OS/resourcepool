package vdiskstorage

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// VdiskstorageAPI is API implementation of /vdiskstorage root endpoint
type VdiskstorageAPI struct {
	AysRepo string
	AysUrl  string
}

func NewVdiskStorageAPI(repo string, aysurl string) VdiskstorageAPI {
	return VdiskstorageAPI{
		AysRepo: repo,
		AysUrl:  aysurl,
	}
}
func (api VdiskstorageAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api VdiskstorageAPI) AysRepoName() string {
	return api.AysRepo
}
