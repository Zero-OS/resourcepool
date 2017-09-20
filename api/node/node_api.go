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
	ApplicationID string
	Secret        string
	Org           string
	Token         string
}

func NewNodeAPI(repo string, aysurl string, applicationID string, secret string, org string, c *cache.Cache) *NodeAPI {
	return &NodeAPI{
		AysRepo:       repo,
		AysURL:        aysurl,
		Cache:         c,
		ApplicationID: applicationID,
		Secret:        secret,
		Org:           org,
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

func (api *NodeAPI) GetAysToken() (string, error) {
	token, err := tools.GetToken(api.Token, api.ApplicationID, api.Secret, api.Org)
	if err != nil {
		return "", err
	}
	api.Token = token
	return token, nil
}

func (api *NodeAPI) ContainerCache() *cache.Cache {
	return api.Cache
}
