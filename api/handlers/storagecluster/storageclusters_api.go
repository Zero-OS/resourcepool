package storagecluster

import (
	"github.com/zero-os/0-orchestrator/api/ays"
)

// StorageclusterAPI is API implementation of /storagecluster root endpoint
type StorageclustersAPI struct {
	client *ays.Client
	// AysRepo       string
	// AysUrl        string
	// ApplicationID string
	// Secret        string
	// Token         string
	// Org           string
}

// func NewStorageClusterAPI(repo string, aysurl string, applicationID string, secret string, org string) *StorageclustersAPI {
func NewStorageClusterAPI(client *ays.Client) *StorageclustersAPI {
	return &StorageclustersAPI{
		client: client,
		// AysRepo:       repo,
		// AysUrl:        aysurl,
		// ApplicationID: applicationID,
		// Secret:        secret,
		// Org:           org,
	}
}

// func (api *StorageclustersAPI) AysAPIClient() *ays.AtYourServiceAPI {
// 	aysAPI := ays.NewAtYourServiceAPI()
// 	aysAPI.BaseURI = api.AysUrl
// 	return aysAPI
// }

// func (api *StorageclustersAPI) AysRepoName() string {
// 	return api.AysRepo
// }

// func (api *StorageclustersAPI) GetAysToken() (string, error) {
// 	token, err := tools.GetToken(api.Token, api.ApplicationID, api.Secret, api.Org)
// 	if err != nil {
// 		return "", err
// 	}
// 	api.Token = token
// 	return token, nil
// }
