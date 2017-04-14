package node

import (
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// ExitZerotier is the handler for DELETE /node/{nodeid}/zerotiers/{zerotierid}
// Exit the Zerotier network
func (api NodeAPI) ExitZerotier(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeID := mux.Vars(r)["nodeid"]
	zerotierID := vars["zerotierid"]

	// execute the exit action of the zerotier
	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			"action":  "delete",
			"actor":   "zerotier",
			"service": fmt.Sprintf("%s_%s", nodeID, zerotierID),
			"force":   true,
		}},
	}

	// And execute
	run, err := tools.ExecuteBlueprint(api.AysRepo, "zerotier", zerotierID, "delete", bp)

	if err != nil {
		log.Errorf("error executing blueprint for zerotier %s exit : %+v", zerotierID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if err := tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err)
		}
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
