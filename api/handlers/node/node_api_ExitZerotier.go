package node

import (
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
)

// ExitZerotier is the handler for DELETE /node/{nodeid}/zerotiers/{zerotierid}
// Exit the Zerotier network
func (api *NodeAPI) ExitZerotier(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	nodeID := mux.Vars(r)["nodeid"]
	zerotierID := vars["zerotierid"]

	// execute the exit action of the zerotier
	bp := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "delete",
			Actor:   "zerotier",
			Service: fmt.Sprintf("%s_%s", nodeID, zerotierID),
			Force:   true,
		}},
	}

	// And execute
	bpName := ays.BlueprintName("zerotier", zerotierID, "delete")
	if _, err := api.client.CreateExecRun(bpName, bp, true); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "zerotier", zerotierID, "delete", bp)

	// errmsg := fmt.Sprintf("error executing blueprint for zerotier %s exit ", zerotierID)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// // Wait for the delete job to be finshed before we delete the service
	// if _, err := aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	errmsg := fmt.Sprintf("error running blueprint for zerotier %s exit ", zerotierID)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	}
	// 	return
	// }

	if err := api.client.DeleteService("zerotier", fmt.Sprintf("%s_%s", nodeID, zerotierID)); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// res, err := aysClient.Ays.DeleteServiceByName(fmt.Sprintf("%s_%s", nodeID, zerotierID), "zerotier", api.AysRepo, nil, nil)

	// if !tools.HandleAYSResponse(err, res, w, fmt.Sprintf("Exiting zerotier %s", fmt.Sprintf("%s_%s", nodeID, zerotierID))) {
	// 	return
	// }

	w.WriteHeader(http.StatusNoContent)
}
