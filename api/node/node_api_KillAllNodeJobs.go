package node

import (
	"net/http"

	"github.com/zero-os/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// KillAllNodeJobs is the handler for DELETE /nodes/{nodeid}/job
// Kills all running jobs
func (api NodeAPI) KillAllNodeJobs(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(cl)

	if err := core.KillAllJobs(); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
