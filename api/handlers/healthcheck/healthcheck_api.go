package healthcheck

import (
	"github.com/zero-os/0-orchestrator/api/ays"
)

// HealthCheckApi is API implementation of /health root endpoint
type HealthCheckApi struct {
	client *ays.Client
}

func NewHealthcheckAPI(aysCl *ays.Client) *HealthCheckApi {
	return &HealthCheckApi{
		client: aysCl,
	}
}
