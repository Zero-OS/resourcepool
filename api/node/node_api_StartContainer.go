package node

import (
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// StartContainer is the handler for POST /nodes/{nodeid}/containers/{containername}/start
// Start Container instance
func (api *NodeAPI) StartContainer(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	containername := vars["containername"]

	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "start",
			Actor:   "container",
			Service: containername,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "container", containername, "start", bp)
	errmsg := fmt.Sprintf("Error executing blueprint for starting container %s ", containername)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	// Wait for the job to be finshed
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for starting container")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for starting container")
		}
		return
	}

	w.WriteHeader(http.StatusCreated)
}
