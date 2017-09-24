package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
)

// DeleteContainer is the handler for DELETE /nodes/{nodeid}/containers/{containername}
// Delete Container instance
func (api *NodeAPI) DeleteContainer(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	api.client.DeleteContainerId(r)
	// tools.DeleteContainerId(r, api)

	vars := mux.Vars(r)
	containerName := vars["containername"]

	// execute the delete action of the snapshot
	blueprint := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "stop",
			Actor:   "container",
			Service: containerName,
			Force:   true,
		}},
	}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "container", containername, "stop", bp)
	// errmsg := "Error executing blueprint for container deletion"
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// // Wait for the delete job to be finshed before we delete the service
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for container deletion")
	// 	}
	// 	return
	// }
	blueprintName := ays.BlueprintName("container", containerName, "stop")
	_, err := api.client.CreateExecRun(blueprintName, blueprint, true)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	// res, err := aysClient.Ays.DeleteServiceByName(containername, "container", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "deleting service") {
	// 	return
	// }
	if err := api.client.DeleteService("container", containerName); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
