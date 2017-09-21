package graph

import (
	"github.com/zero-os/0-orchestrator/api/ays"
)

// GraphAPI is API implementation of /graphs root endpoint
type GraphAPI struct {
	client *ays.Client
	// AysRepo       string
	// AysUrl        string
	// Cache         *cache.Cache
	// ApplicationID string
	// Secret        string
	// Token         string
	// Org           string
}

func NewGraphAPI(client *ays.Client) *GraphAPI {
	return &GraphAPI{
		client: client,
		// AysRepo:       repo,
		// AysUrl:        aysurl,
		// Cache:         c,
		// ApplicationID: applicationID,
		// Secret:        secret,
		// Org:           org,
	}
}

// func (api *GraphAPI) AysAPIClient() *ays.AtYourServiceAPI {
// 	aysAPI := ays.NewAtYourServiceAPI()
// 	aysAPI.BaseURI = api.AysUrl
// 	return aysAPI
// }

// func (api *GraphAPI) AysRepoName() string {
// 	return api.AysRepo
// }

// func (api *GraphAPI) ContainerCache() *cache.Cache {
// 	return api.Cache
// }

// func (api *GraphAPI) GetAysToken() (string, error) {
// 	token, err := tools.GetToken(api.Token, api.ApplicationID, api.Secret, api.Org)
// 	if err != nil {
// 		return "", err
// 	}
// 	api.Token = token
// 	return token, nil
// }
