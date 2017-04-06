package storagecluster

import ays "github.com/g8os/grid/api/ays-client"

// StorageclusterAPI is API implementation of /storagecluster root endpoint
type StorageclusterAPI struct {
	AysRepo string
	AysAPI  *ays.AtYourServiceAPI
}

func NewStorageClusterAPI(repo string, client *ays.AtYourServiceAPI) StorageclusterAPI {
	return StorageclusterAPI{
		AysRepo: repo,
		AysAPI:  client,
	}
}
