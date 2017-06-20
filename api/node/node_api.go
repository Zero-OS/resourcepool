package node

import (
	"github.com/patrickmn/go-cache"
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// NodeAPI is API implementation of /node root endpoint
type NodeAPI struct {
	AysRepo string
	AysUrl  string
	Cache   *cache.Cache
}

func NewNodeAPI(repo string, aysurl string, c *cache.Cache) NodeAPI {
	return NodeAPI{
		AysRepo: repo,
		AysUrl:  aysurl,
		Cache:   c,
	}
}

func (api NodeAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api NodeAPI) AysRepoName() string {
	return api.AysRepo
}

func (api NodeAPI) ContainerCache() *cache.Cache {
	return api.Cache
}
