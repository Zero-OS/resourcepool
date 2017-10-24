package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteBridge is the handler for DELETE /node/{nodeid}/bridge/{bridgeid}
// Remove bridge
func (api *NodeAPI) DeleteBridge(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	bridge := vars["bridgeid"]

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "delete",
			Actor:   "bridge",
			Service: bridge,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "bridge", bridge, "delete", blueprint)
	errmsg := "Error executing blueprint for bridge deletion "
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for bridge deletion")
		}
		return
	}

	res, err := aysClient.Ays.DeleteServiceByName(bridge, "bridge", api.AysRepo, nil, nil)
	if !tools.HandleAYSDeleteResponse(err, res, w, "deleting service") {
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
