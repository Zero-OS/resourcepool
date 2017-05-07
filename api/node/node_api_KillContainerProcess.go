package node

import (
	"net/http"

	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// KillContainerProcess is the handler for DELETE /nodes/{nodeid}/containers/{containername}/processes/{processid}
// Kill Process
func (api NodeAPI) KillContainerProcess(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)

	cl, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	tools.KillProcess(vars["processid"], cl, w)
}
