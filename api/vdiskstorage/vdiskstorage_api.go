package vdiskstorage

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// VdiskstorageAPI is API implementation of /vdiskstorage root endpoint
type VdiskstorageAPI struct {
	AysRepo     string
	AysUrl      string
	AysRetries  string
	JWTProvider *tools.JWTProvider
}

func NewVdiskStorageAPI(repo string, aysUrl string, aysRetries string, jwtProvider *tools.JWTProvider) *VdiskstorageAPI {
	return &VdiskstorageAPI{
		AysRepo:     repo,
		AysUrl:      aysUrl,
		AysRetries:  aysRetries,
		JWTProvider: jwtProvider,
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

func (api *VdiskstorageAPI) GetJWT() (string, error) {
	return api.JWTProvider.GetJWT()
}

func (api *VdiskstorageAPI) AysRetriesConfig() string {
	return api.AysRetries
}
