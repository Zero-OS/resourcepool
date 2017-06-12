package run

import (
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	_ "github.com/zero-os/0-orchestrator/api/validators"
)

// RunsAPI is API implementation of /runs root endpoint
type RunsAPI struct {
	AysRepo string
	AysAPI  *ays.AtYourServiceAPI
}

func NewRunAPI(repo string, client *ays.AtYourServiceAPI) RunsAPI {
	return RunsAPI{
		AysRepo: repo,
		AysAPI:  client,
	}
}
