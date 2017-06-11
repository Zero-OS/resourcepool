package node

import (
	"fmt"
	"net/http"
	"syscall"

	"github.com/gorilla/mux"
	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// KillContainerJob is the handler for DELETE /nodes/{nodeid}/container/{containername}/job/{jobid}
// Kills the job
func (api NodeAPI) KillContainerJob(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := client.JobId(vars["jobid"])

	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}
	core := client.Core(container)

	if err := core.KillJob(jobID, syscall.SIGKILL); err != nil {
		errmsg := fmt.Sprintf("Error killing job %s on node", jobID)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
