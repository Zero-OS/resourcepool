package node

import (
	"net/http"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// KillAllContainerJobs is the handler for DELETE /nodes/{nodeid}/container/{containername}/job
// Kills all running jobs on the container
func (api NodeAPI) KillAllContainerJobs(w http.ResponseWriter, r *http.Request) {
	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(container)

	if err := core.KillAllJobs(); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
