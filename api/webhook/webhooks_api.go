package webhook

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// WebhooksAPI is API implementation of /webhooks root endpoint
type WebhooksAPI struct {
	AysRepo     string
	AysUrl      string
	JWTProvider *tools.JWTProvider
}

func NewWebhookAPI(repo string, aysurl string, jwtProvider *tools.JWTProvider) *WebhooksAPI {
	return &WebhooksAPI{
		AysRepo:     repo,
		AysUrl:      aysurl,
		JWTProvider: jwtProvider,
	}
}

func (api *WebhooksAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api *WebhooksAPI) AysRepoName() string {
	return api.AysRepo
}

func (api *WebhooksAPI) GetJWT() (string, error) {
	return api.JWTProvider.GetJWT()
}
