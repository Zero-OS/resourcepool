package vdisk

import (
	"github.com/zero-os/0-orchestrator/api/ays"
)

// VdisksAPI is API implementation of /vdisks root endpoint
type VdisksAPI struct {
	client *ays.Client
	// AysRepo       string
	// AysUrl        string
	// ApplicationID string
	// Secret        string
	// Token         string
	// Org           string
}

func NewVdiskAPI(aysCl *ays.Client) *VdisksAPI {
	return &VdisksAPI{
		client: aysCl,
		// AysRepo:       repo,
		// AysUrl:        aysurl,
		// ApplicationID: applicationID,
		// Secret:        secret,
		// Org:           org,
	}
}

// func (api *VdisksAPI) AysAPIClient() *ays.AtYourServiceAPI {
// 	aysAPI := ays.NewAtYourServiceAPI()
// 	aysAPI.BaseURI = api.AysUrl
// 	return aysAPI
// }

// func (api *VdisksAPI) AysRepoName() string {
// 	return api.AysRepo
// }

// func (api *VdisksAPI) GetAysToken() (string, error) {
// 	token, err := tools.GetToken(api.Token, api.ApplicationID, api.Secret, api.Org)
// 	if err != nil {
// 		return "", err
// 	}
// 	api.Token = token
// 	return token, nil
// }
