package backup

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// BackupAPI is API implementation of /backup root endpoint
type BackupAPI struct {
	AysRepo string
	AysUrl  string
}

func NewBackupAPI(repo string, aysurl string) BackupAPI {
	return BackupAPI{
		AysRepo: repo,
		AysUrl:  aysurl,
	}
}

func (api BackupAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api BackupAPI) AysRepoName() string {
	return api.AysRepo
}
