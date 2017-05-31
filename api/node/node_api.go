package node

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	_ "github.com/zero-os/0-orchestrator/api/validators"
	"github.com/patrickmn/go-cache"
)

// NodeAPI is API implementation of /node root endpoint
type NodeAPI struct {
	AysRepo string
	AysAPI  *ays.AtYourServiceAPI
	Cache   *cache.Cache
}

func NewNodeAPI(repo string, client *ays.AtYourServiceAPI, c *cache.Cache) NodeAPI {
	return NodeAPI{
		AysRepo: repo,
		AysAPI:  client,
		Cache:   c,
	}
}

func (api NodeAPI) AysAPIClient() *ays.AtYourServiceAPI {
	return api.AysAPI
}

func (api NodeAPI) AysRepoName() string {
	return api.AysRepo
}

func (api NodeAPI) ContainerCache() *cache.Cache {
	return api.Cache
}
