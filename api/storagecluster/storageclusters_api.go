package storagecluster

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// StorageclusterAPI is API implementation of /storagecluster root endpoint
type StorageclustersAPI struct {
	AysRepo string
	AysUrl  string
}

func NewStorageClusterAPI(repo string, aysurl string) StorageclustersAPI {
	return StorageclustersAPI{
		AysRepo: repo,
		AysUrl:  aysurl,
	}
}

func (api StorageclustersAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api StorageclustersAPI) AysRepoName() string {
	return api.AysRepo
}
