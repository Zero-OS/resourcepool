package vdisk

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	tools "github.com/zero-os/0-orchestrator/api/tools"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// VdisksAPI is API implementation of /vdisks root endpoint
type VdisksAPI struct {
	AysRepo       string
	AysUrl        string
	JWTProvider   *tools.JWTProvider
}

func NewVdiskAPI(repo string, aysurl string, jwtProvider *tools.JWTProvider) *VdisksAPI {
	return &VdisksAPI{
		AysRepo:       repo,
		AysUrl:        aysurl,
		JWTProvider:    jwtProvider,
	}
}

func (api *VdisksAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api *VdisksAPI) AysRepoName() string {
	return api.AysRepo
}

func (api *VdisksAPI) GetJWT() (string, error) {
        return api.JWTProvider.GetToken()
}

