package node

import (
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// StartContainer is the handler for POST /nodes/{nodeid}/containers/{containerid}/start
// Start Container instance
func (api NodeAPI) StartContainer(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	containerID := vars["containerid"]

	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			"action":  "start",
			"actor":   "container",
			"service": containerID,
			"force":   true,
		}},
	}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "container", containerID, "start", bp)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for starting container %s : %+v", containerID, err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		return
	}

	// Wait for the job to be finshed
	if err = tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err)
		}
		return
	}

	w.WriteHeader(http.StatusCreated)
}
