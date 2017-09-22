package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// KillNodeProcess is the handler for DELETE /nodes/{nodeid}/processes/{processid}
// Kill Process
func (api *NodeAPI) KillNodeProcess(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)

	nodeCl, err := api.client.GetNodeConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	err = api.client.KillProcess(vars["processid"], nodeCl)
	if err != nil {
		if err == ays.ErrBadProcessId {
			httperror.WriteError(w, http.StatusBadRequest, err, err.Error())
		} else {
			httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
		}
	}

	w.WriteHeader(http.StatusNoContent)
}
