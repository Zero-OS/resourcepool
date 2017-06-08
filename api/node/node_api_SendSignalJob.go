package node

import (
	"encoding/json"
	"net/http"
	"syscall"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// SendSignalJob is the handler for POST /nodes/{nodeid}/containers/{containername}/job
// Send signal to the job
func (api NodeAPI) SendSignalJob(w http.ResponseWriter, r *http.Request) {
	var reqBody ProcessSignal

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// Get a container connection
	cl, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "")
		return
	}

	jobId := mux.Vars(r)["jobId"]
	core := client.Core(cl)

	// Send signal to the container
	if err := core.KillJob(client.JobId(jobId), syscall.Signal(reqBody.Signal)); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "")
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
