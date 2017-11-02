package graph

import (
	"github.com/patrickmn/go-cache"
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	tools "github.com/zero-os/0-orchestrator/api/tools"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// GraphAPI is API implementation of /graphs root endpoint
type GraphAPI struct {
	AysRepo     string
	AysUrl      string
	AysRetries  string
	Cache       *cache.Cache
	JWTProvider *tools.JWTProvider
}

func NewGraphAPI(repo string, aysUrl string, aysRetries string, jwtProvider *tools.JWTProvider, c *cache.Cache) *GraphAPI {
	return &GraphAPI{
		AysRepo:     repo,
		AysUrl:      aysUrl,
		AysRetries:  aysRetries,
		Cache:       c,
		JWTProvider: jwtProvider,
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
	return api.JWTProvider.GetJWT()
}

func (api *GraphAPI) AysRetriesConfig() string {
	return api.AysRetries
}
