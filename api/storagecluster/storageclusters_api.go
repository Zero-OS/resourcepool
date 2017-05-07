package storagecluster

import (
	"time"

	ays "github.com/g8os/grid/api/ays-client"
	"github.com/patrickmn/go-cache"
        _ "github.com/g8os/grid/api/validators"
)

// StorageclusterAPI is API implementation of /storagecluster root endpoint
type StorageclustersAPI struct {
	AysRepo string
	AysAPI  *ays.AtYourServiceAPI
	cache   *cache.Cache
}

func NewStorageClusterAPI(repo string, client *ays.AtYourServiceAPI) StorageclustersAPI {
	return StorageclustersAPI{
		AysRepo: repo,
		AysAPI:  client,
		cache:   cache.New(10*time.Minute, 30*time.Minute),
	}
}
