package node

import (
	"net/http"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// StopGateway is the handler for POST /nodes/{nodeid}/gws/{gwname}/stop
// Stop gateway instance
func (api *NodeAPI) StopGateway(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	gwID := vars["gwname"]

	exists, err := aysClient.ServiceExists("gateway", gwID, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking gateway service exists")
		return
	} else if !exists {
		err = fmt.Errorf("Gateway with name %s doesn't exists", gwID)
		tools.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "stop",
			Actor:   "gateway",
			Service: gwID,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "stop", bp)
	errmsg := fmt.Sprintf("Error executing blueprint for stoping gateway %s", gwID)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	// Wait for the job to be finshed
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("Error running blueprint for stoping gateway %s", gwID)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		}
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
