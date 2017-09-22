package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// KillContainerProcess is the handler for DELETE /nodes/{nodeid}/containers/{containername}/processes/{processid}
// Kill Process
func (api *NodeAPI) KillContainerProcess(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)

	cl, err := tools.GetContainerConnection(r, api)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	tools.KillProcess(vars["processid"], cl, w)
}
