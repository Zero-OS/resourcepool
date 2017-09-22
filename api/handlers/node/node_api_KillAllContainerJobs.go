package node

import (
	"net/http"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// KillAllContainerJobs is the handler for DELETE /nodes/{nodeid}/container/{containername}/job
// Kills all running jobs on the container
func (api *NodeAPI) KillAllContainerJobs(w http.ResponseWriter, r *http.Request) {
	container, err := api.client.GetContainerConnection(r, api)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	core := client.Core(container)

	if err := core.KillAllJobs(); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error killing all jobs")
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
