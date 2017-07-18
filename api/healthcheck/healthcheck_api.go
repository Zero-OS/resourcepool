package healthcheck

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
)

// HealthCheckApi is API implementation of /health root endpoint
type HealthCheckApi struct {
	AysRepo string
	AysUrl  string
}

func (api HealthCheckApi) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api HealthCheckApi) AysRepoName() string {
	return api.AysRepo
}

func NewHealthcheckAPI(repo string, aysurl string) HealthCheckApi {
	return HealthCheckApi{
		AysRepo: repo,
		AysUrl:  aysurl,
	}
}
