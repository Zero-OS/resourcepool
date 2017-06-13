package node

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
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
	api.AysAPI.AuthHeader = r.Header.Get("Authorization")
	run, err := tools.ExecuteBlueprint(api.AysRepo, "zerotier", zerotierID, "delete", bp)

	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for zerotier %s exit ", zerotierID)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if err := tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error running blueprint for zerotier %s exit ", zerotierID)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		}
		return
	}

	res, err := api.AysAPI.Ays.DeleteServiceByName(fmt.Sprintf("%s_%s", nodeID, zerotierID), "zerotier", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, fmt.Sprintf("Exiting zerotier %s", fmt.Sprintf("%s_%s", nodeID, zerotierID))) {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
