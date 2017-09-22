package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// KillContainerProcess is the handler for DELETE /nodes/{nodeid}/containers/{containername}/processes/{processid}
// Kill Process
func (api *NodeAPI) KillContainerProcess(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)

	// cl, err := tools.GetContainerConnection(r, api)
	containerConnection, err := api.client.GetContainerConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	if err := api.client.KillProcess(vars["processid"], containerConnection); err != nil {
		handlers.HandleError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
	// tools.KillProcess(vars["processid"], cl, w)
}
