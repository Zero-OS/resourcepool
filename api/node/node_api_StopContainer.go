package node

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// StopContainer is the handler for POST /nodes/{nodeid}/containers/{containername}/stop
// Stop Container instance
func (api NodeAPI) StopContainer(w http.ResponseWriter, r *http.Request) {
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

	run, err := tools.ExecuteBlueprint(api.AysRepo, "container", containername, "stop", bp)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("Error executing blueprint for stopping container %s ", containername)
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		return
	}

	// Wait for the job to be finshed
	if err = tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "")
		}
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
