package node

import (
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
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
		fmt.Errorf("Error executing blueprint for starting gateway %s : %+v", gwID, err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		return
	}

	// Wait for the job to be finshed
	if err = tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "")
		}
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
