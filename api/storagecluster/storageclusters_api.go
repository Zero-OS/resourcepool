package storagecluster

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	tools "github.com/zero-os/0-orchestrator/api/tools"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// StorageclusterAPI is API implementation of /storagecluster root endpoint
type StorageclustersAPI struct {
	AysRepo     string
	AysUrl      string
	JWTProvider *tools.JWTProvider
}

func NewStorageClusterAPI(repo string, aysurl string, jwtProvider *tools.JWTProvider) *StorageclustersAPI {
	return &StorageclustersAPI{
		AysRepo:     repo,
		AysUrl:      aysurl,
		JWTProvider: jwtProvider,
	}
}

func (api *StorageclustersAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api *StorageclustersAPI) AysRepoName() string {
	return api.AysRepo
}

func (api *StorageclustersAPI) GetJWT() (string, error) {
	return api.JWTProvider.GetJWT()
}
