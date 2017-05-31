package node

import (
	"net/http"
	"syscall"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// KillContainerJob is the handler for DELETE /nodes/{nodeid}/container/{containername}/job/{jobid}
// Kills the job
func (api NodeAPI) KillContainerJob(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := client.JobId(vars["jobid"])

	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	core := client.Core(container)

	if err := core.KillJob(jobID, syscall.SIGKILL); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
