package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// KillNodeProcess is the handler for DELETE /nodes/{nodeid}/processes/{processid}
// Kill Process
func (api *NodeAPI) KillNodeProcess(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)

	cl, err := tools.GetConnection(r, api)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	tools.KillProcess(vars["processid"], cl, w)
}
