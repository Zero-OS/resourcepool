package healthcheck

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// HealthCheckApi is API implementation of /health root endpoint
type HealthCheckApi struct {
	AysRepo       string
	AysUrl        string
	ApplicationID string
	Secret        string
	Token         string
	Org           string
}

func (api *HealthCheckApi) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api *HealthCheckApi) AysRepoName() string {
	return api.AysRepo
}

func NewHealthcheckAPI(repo string, aysurl string, applicationID string, secret string, org string) *HealthCheckApi {
	return &HealthCheckApi{
		AysRepo:       repo,
		AysUrl:        aysurl,
		ApplicationID: applicationID,
		Secret:        secret,
		Org:           org,
	}
}

func (api *HealthCheckApi) GetAysToken() (string, error) {
	token, err := tools.GetToken(api.Token, api.ApplicationID, api.Secret, api.Org)
	if err != nil {
		return "", err
	}
	api.Token = token
	return token, nil
}
