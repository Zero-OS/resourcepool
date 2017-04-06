package node

import (
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// KillContainerJob is the handler for DELETE /node/{nodeid}/container/{containerid}/job/{jobid}
// Kills the job
func (api NodeAPI) KillContainerJob(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := client.Job(vars["jobid"])

	container, err := tools.GetContainerConnection(r)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	core := client.Core(container)

	if err := core.Kill(jobID); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
