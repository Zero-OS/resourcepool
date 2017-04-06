package node

import (
	"fmt"
	"net/http"
	"time"

	log "github.com/Sirupsen/logrus"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// DeleteBridge is the handler for DELETE /node/{nodeid}/bridge/{bridgeid}
// Remove bridge
func (api NodeAPI) DeleteBridge(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	bridge := vars["bridgeid"]

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []map[string]string{{
			"action":  "delete",
			"actor":   "bridge",
			"service": bridge,
		}},
	}
	blueprintName := fmt.Sprintf("bridge__%s_delete_%d", bridge, time.Now().Unix())

	run, err := tools.ExecuteBlueprint(api.AysRepo, blueprintName, blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for bridge deletion : %+v", err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if err = tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err)
		}
		return
	}

	_, err = api.AysAPI.Ays.DeleteServiceByName(bridge, "bridge", api.AysRepo, nil, nil)

	if err != nil {
		log.Errorf("Error in deleting bridge %s : %+v", bridge, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
