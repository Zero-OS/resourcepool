package node

import (
	"encoding/json"
	"net/http"
	"syscall"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
	"strconv"
)

// SendSignalProcess is the handler for POST /nodes/{nodeid}/containers/{containername}/processes/{processid}
// Send signal to the process
func (api NodeAPI) SendSignalProcess(w http.ResponseWriter, r *http.Request) {
	var reqBody ProcessSignal

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	vars := mux.Vars(r)
	pId, err := strconv.ParseUint(vars["processid"], 10, 64)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	processId := client.ProcessId(pId)

	// Get container connection
	cl, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	// Send signal to the container process
	core := client.Core(cl)
	if err := core.KillProcess(processId, syscall.Signal(reqBody.Signal)); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
