package vdisk

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// VdisksAPI is API implementation of /vdisks root endpoint
type VdisksAPI struct {
	AysRepo       string
	AysUrl        string
	ApplicationID string
	Secret        string
	Token         string
	Org           string
}

func NewVdiskAPI(repo string, aysurl string, applicationID string, secret string, org string) *VdisksAPI {
	return &VdisksAPI{
		AysRepo:       repo,
		AysUrl:        aysurl,
		ApplicationID: applicationID,
		Secret:        secret,
		Org:           org,
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

func (api *VdisksAPI) GetAysToken() (string, error) {
	token, err := tools.GetToken(api.Token, api.ApplicationID, api.Secret, api.Org)
	if err != nil {
		return "", err
	}
	api.Token = token
	return token, nil
}
