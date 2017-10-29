package healthcheck

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	tools "github.com/zero-os/0-orchestrator/api/tools"
)

// HealthCheckApi is API implementation of /health root endpoint
type HealthCheckApi struct {
	AysRepo     string
	AysUrl      string
	JWTProvider *tools.JWTProvider
}

func (api *HealthCheckApi) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api *HealthCheckApi) AysRepoName() string {
	return api.AysRepo
}

func NewHealthcheckAPI(repo string, aysurl string, jwtProvider *tools.JWTProvider) *HealthCheckApi {
	return &HealthCheckApi{
		AysRepo:     repo,
		AysUrl:      aysurl,
		JWTProvider: jwtProvider,
	}
}

func (api *HealthCheckApi) GetJWT() (string, error) {
	return api.JWTProvider.GetJWT()
}
