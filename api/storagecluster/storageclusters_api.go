package storagecluster

import (
	ays "github.com/g8os/grid/api/ays-client"
	_ "github.com/g8os/grid/api/validators"
)

// StorageclusterAPI is API implementation of /storagecluster root endpoint
type StorageclustersAPI struct {
	AysRepo string
	AysAPI  *ays.AtYourServiceAPI
}

func NewStorageClusterAPI(repo string, client *ays.AtYourServiceAPI) StorageclustersAPI {
	return StorageclustersAPI{
		AysRepo: repo,
		AysAPI:  client,
	}
}
