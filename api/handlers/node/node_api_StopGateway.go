package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// StopGateway is the handler for POST /nodes/{nodeid}/gws/{gwname}/stop
// Stop gateway instance
func (api *NodeAPI) StopGateway(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	gwID := vars["gwname"]

	exists, err := api.client.IsServiceExists("gatway", gwID)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	// exists, err := aysClient.ServiceExists("gateway", gwID, api.AysRepo)
	// if err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error checking gateway service exists")
	// 	return
	// } else
	if !exists {
		err = fmt.Errorf("Gateway with name %s doesn't exists", gwID)
		httperror.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	bp := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "stop",
			Actor:   "gateway",
			Service: gwID,
			Force:   true,
		}},
	}
	bpName := ays.BlueprintName("gateway", gwID, "stop")
	if err := api.client.CreateExec(bpName, bp); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "stop", bp)
	// errmsg := fmt.Sprintf("Error executing blueprint for stoping gateway %s", gwID)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// // Wait for the job to be finshed
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	errmsg := fmt.Sprintf("Error running blueprint for stoping gateway %s", gwID)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	}
	// 	return
	// }
	w.WriteHeader(http.StatusNoContent)
}
