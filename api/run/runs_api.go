package run

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// RunsAPI is API implementation of /runs root endpoint
type RunsAPI struct {
	AysRepo string
	AysUrl  string
}

func NewRunAPI(repo string, aysurl string) RunsAPI {
	return RunsAPI{
		AysRepo: repo,
		AysUrl:  aysurl,
	}
}

func (api RunsAPI) AysAPIClient() *ays.AtYourServiceAPI {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = api.AysUrl
	return aysAPI
}

func (api RunsAPI) AysRepoName() string {
	return api.AysRepo
}
