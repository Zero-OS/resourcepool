package node

import (
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// StopContainer is the handler for POST /nodes/{nodeid}/containers/{containername}/stop
// Stop Container instance
func (api *NodeAPI) StopContainer(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	api.client.DeleteContainerId(r)

	vars := mux.Vars(r)
	containername := vars["containername"]
	// execute the delete action of the snapshot
	bp := ays.Blueprint{
		"actions": []tools.ActionBlock{{
			Action:  "stop",
			Actor:   "container",
			Service: containername,
			Force:   true,
		}},
	}

	if err := api.client.CreateExec(bpName, bp); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "container", containername, "stop", bp)
	// errmsg := fmt.Sprintf("Error executing blueprint for stopping container %s ", containername)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// // Wait for the job to be finshed
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	errmsg := fmt.Sprintf("Error running blueprint for stopping container %s ", containername)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	}
	// 	return
	// }

	w.WriteHeader(http.StatusNoContent)
}
