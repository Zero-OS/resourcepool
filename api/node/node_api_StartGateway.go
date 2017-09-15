package node

import (
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// StartGateway is the handler for POST /nodes/{nodeid}/gws/{gwname}/start
// Start Gateway instance
func (api *NodeAPI) StartGateway(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	gwID := vars["gwname"]

	exists, err := aysClient.ServiceExists("gateway", gwID, api.AysRepo)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error checking gateway service exists")
		return
	} else if !exists {
		err = fmt.Errorf("Gateway with name %s doesn't exists", gwID)
		httperror.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "start",
			Actor:   "gateway",
			Service: gwID,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "start", bp)

	errmsg := fmt.Sprintf("Error executing blueprint for starting gateway %s", gwID)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	// Wait for the job to be finshed
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(httperror.HTTPError)
		if ok {
			httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error executing blueprint for starting gateway")
		} else {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error executing blueprint for starting gateway")
		}
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
