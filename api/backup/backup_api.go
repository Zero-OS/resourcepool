package backup

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// BackupAPI is API implementation of /backup root endpoint
type BackupAPI struct {
	AysRepo       string
	AysUrl        string
	ApplicationID string
	Secret        string
	Token         string
	Org           string
}

func NewBackupAPI(repo string, aysurl string, applicationID string, secret string, org string) *BackupAPI {
	return &BackupAPI{
		AysRepo:       repo,
		AysUrl:        aysurl,
		ApplicationID: applicationID,
		Secret:        secret,
		Org:           org,
	}
}

func (api *BackupAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api *BackupAPI) AysRepoName() string {
	return api.AysRepo
}

func (api *BackupAPI) GetAysToken() (string, error) {
	token, err := tools.GetToken(api.Token, api.ApplicationID, api.Secret, api.Org)
	if err != nil {
		return "", err
	}
	api.Token = token
	return token, nil
}
