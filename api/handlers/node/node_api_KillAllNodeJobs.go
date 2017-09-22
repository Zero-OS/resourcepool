package node

import (
	"net/http"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// KillAllNodeJobs is the handler for DELETE /nodes/{nodeid}/job
// Kills all running jobs
func (api *NodeAPI) KillAllNodeJobs(w http.ResponseWriter, r *http.Request) {
	cl, err := api.client.GetNodeConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	core := client.Core(cl)

	if err := core.KillAllJobs(); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error killing all jobs")
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
