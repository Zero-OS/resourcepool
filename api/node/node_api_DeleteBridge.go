package node

import (
	"net/http"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteBridge is the handler for DELETE /node/{nodeid}/bridge/{bridgeid}
// Remove bridge
func (api NodeAPI) DeleteBridge(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	bridge := vars["bridgeid"]

	exists, err := aysClient.ServiceExists("bridge", bridge, api.AysRepo)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to check for the bridge")
		return
	}

	if !exists {
		err = fmt.Errorf("Bridge %s doesn't exist", bridge)
		tools.WriteError(w, http.StatusNotFound, err, err.Error())
		return
	}

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
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := "Error executing blueprint for bridge deletion "
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for bridge deletion")
		}
		return
	}

	_, err = aysClient.Ays.DeleteServiceByName(bridge, "bridge", api.AysRepo, nil, nil)

	if err != nil {
		errmsg := fmt.Sprintf("Error in deleting bridge %s ", bridge)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
