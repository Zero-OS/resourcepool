package graph

import (
	"github.com/patrickmn/go-cache"
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	tools "github.com/zero-os/0-orchestrator/api/tools"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// GraphAPI is API implementation of /graphs root endpoint
type GraphAPI struct {
	AysRepo       string
	AysUrl        string
	Cache         *cache.Cache
	JWTProvider   *tools.JWTProvider
}

func NewGraphAPI(repo string, aysurl string, jwtProvider *tools.JWTProvider, c *cache.Cache) *GraphAPI {
	return &GraphAPI{
		AysRepo:       repo,
		AysUrl:        aysurl,
		Cache:         c,
		JWTProvider:   jwtProvider,
	}
}

func (api *GraphAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api *GraphAPI) AysRepoName() string {
	return api.AysRepo
}

func (api *GraphAPI) ContainerCache() *cache.Cache {
	return api.Cache
}

func (api *GraphAPI) GetJWT() (string, error) {
        return api.JWTProvider.GetToken()
}
