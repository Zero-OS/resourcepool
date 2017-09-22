package node

import (
	"github.com/zero-os/0-orchestrator/api/ays"

	"net/http"

	"github.com/gorilla/mux"
)

// StartContainer is the handler for POST /nodes/{nodeid}/containers/{containername}/start
// Start Container instance
func (api *NodeAPI) StartContainer(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	containername := vars["containername"]

	bp := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "start",
			Actor:   "container",
			Service: containername,
			Force:   true,
		}},
	}
	bpName := ays.BlueprintName("container", containername, "strat")
	if _, err := api.client.CreateExecRun(bpName, bp); err != nil {
		handler.HandleError(w, err)
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "container", containername, "start", bp)
	// errmsg := fmt.Sprintf("Error executing blueprint for starting container %s ", containername)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// // Wait for the job to be finshed
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for starting container")
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for starting container")
	// 	}
	// 	return
	// }

	w.WriteHeader(http.StatusCreated)
}
