package node

import (
	"github.com/patrickmn/go-cache"
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	tools "github.com/zero-os/0-orchestrator/api/tools"

	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// NodeAPI is API implementation of /node root endpoint
type NodeAPI struct {
	AysRepo       string
	AysURL        string
	Cache         *cache.Cache
	JWTProvider   *tools.JWTProvider
}

func NewNodeAPI(repo string, aysurl string, jwtProvider *tools.JWTProvider, c *cache.Cache) *NodeAPI {
	return &NodeAPI{
		AysRepo:       repo,
		AysURL:        aysurl,
		Cache:         c,
		JWTProvider:   jwtProvider,
	}
}

func (api *NodeAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysURL
	return aysAPI
}

func (api *NodeAPI) AysRepoName() string {
	return api.AysRepo
}

func (api *NodeAPI) ContainerCache() *cache.Cache {
	return api.Cache
}

func (api *NodeAPI) GetJWT() (string, error) {
	return api.JWTProvider.GetToken()
}
