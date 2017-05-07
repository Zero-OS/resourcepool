package node

import (
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/resourcepool/api/tools"
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
			Action:  "delete",
			Actor:   "zerotier",
			Service: fmt.Sprintf("%s_%s", nodeID, zerotierID),
			Force:   true,
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

	res, err := api.AysAPI.Ays.DeleteServiceByName(fmt.Sprintf("%s_%s", nodeID, zerotierID), "zerotier", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, fmt.Sprintf("Exiting zerotier %s", fmt.Sprintf("%s_%s", nodeID, zerotierID))) {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
