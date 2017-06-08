package node

import (
	"net/http"

	"fmt"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// StopGateway is the handler for POST /nodes/{nodeid}/gws/{gwname}/stop
// Stop gateway instance
func (api NodeAPI) StopGateway(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	gwID := vars["gwname"]

	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "stop",
			Actor:   "gateway",
			Service: gwID,
			Force:   true,
		}},
	}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "stop", bp)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		fmt.Errorf("Error executing blueprint for stoping gateway %s : %+v", gwID, err.Error())
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
