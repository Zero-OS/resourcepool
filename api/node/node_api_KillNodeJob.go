package node

import (
	"net/http"
	"syscall"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// KillNodeJob is the handler for DELETE /nodes/{nodeid}/job/{jobid}
// Kills the job
func (api *NodeAPI) KillNodeJob(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := vars["jobid"]
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	core := client.Core(cl)

	if err := core.KillJob(client.JobId(jobID), syscall.SIGKILL); err != nil {
		errmsg := fmt.Sprintf("Error killing job %s on node", jobID)
		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
