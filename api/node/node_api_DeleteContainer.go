package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteContainer is the handler for DELETE /nodes/{nodeid}/containers/{containername}
// Delete Container instance
func (api *NodeAPI) DeleteContainer(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	tools.DeleteContainerId(r, api)

	vars := mux.Vars(r)
	containername := vars["containername"]

	// execute the delete action of the snapshot
	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "stop",
			Actor:   "container",
			Service: containername,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "container", containername, "stop", bp)
	errmsg := "Error executing blueprint for container deletion"
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(httperror.HTTPError)
		if ok {
			httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for container deletion")
		}
		return
	}

	res, err := aysClient.Ays.DeleteServiceByName(containername, "container", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "deleting service") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
