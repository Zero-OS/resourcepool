package vdiskstorage

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// VdiskstorageAPI is API implementation of /vdiskstorage root endpoint
type VdiskstorageAPI struct {
	AysRepo       string
	AysUrl        string
	ApplicationID string
	Secret        string
	Token         string
	Org           string
}

func NewVdiskStorageAPI(repo string, aysurl string, applicationID string, secret string, org string) *VdiskstorageAPI {
	return &VdiskstorageAPI{
		AysRepo:       repo,
		AysUrl:        aysurl,
		ApplicationID: applicationID,
		Secret:        secret,
		Org:           org,
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

func (api *VdiskstorageAPI) GetAysToken() (string, error) {
	token, err := tools.GetToken(api.Token, api.ApplicationID, api.Secret, api.Org)
	if err != nil {
		return "", err
	}
	api.Token = token
	return token, nil
}
