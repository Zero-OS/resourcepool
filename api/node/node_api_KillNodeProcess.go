package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// KillNodeProcess is the handler for DELETE /nodes/{nodeid}/processes/{processid}
// Kill Process
func (api NodeAPI) KillNodeProcess(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)

	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "")
		return
	}

	tools.KillProcess(vars["processid"], cl, w)
}
