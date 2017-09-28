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
	JWTProvider *tools.JWTProvider
}

func NewVdiskStorageAPI(repo string, aysurl string, jwtProvider *tools.JWTProvider) *VdiskstorageAPI {
	return &VdiskstorageAPI{
		AysRepo:     repo,
		AysUrl:      aysurl,
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
