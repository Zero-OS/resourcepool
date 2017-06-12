package node

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// StartGateway is the handler for POST /nodes/{nodeid}/gws/{gwname}/start
// Start Gateway instance
func (api NodeAPI) StartGateway(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	gwID := vars["gwname"]

	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "start",
			Actor:   "gateway",
			Service: gwID,
			Force:   true,
		}},
	}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "start", bp)

	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("Error executing blueprint for starting gateway %s", gwID)
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		return
	}

	// Wait for the job to be finshed
	if err = tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error executing blueprint for starting gateway")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error executing blueprint for starting gateway")
		}
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
