package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
)

// DeleteNode is the handler for DELETE /nodes/{nodeid}
// Delete Node
func (api *NodeAPI) DeleteNode(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	// execute the uninstall action of the node
	blueprint := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "uninstall",
			Actor:   "node.zero-os",
			Service: nodeID,
			Force:   true,
		}},
	}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "node.zero-os", nodeID, "uninstall", bp)
	// errmsg := "Error executing blueprint for node uninstallation "
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// // Wait for the uninstall job to be finshed before we delete the service
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for node uninstallation")
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for node uninstallation")
	// 	}
	// 	return
	// }

	blueprintName := ays.BlueprintName("node.zero-os", nodeID, "uninstall")
	if _, err := api.client.CreateExecRun(blueprintName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}

	// res, err := aysClient.Ays.DeleteServiceByName(nodeID, "node.zero-os", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "deleting service") {
	// 	return
	// }

	if err := api.client.DeleteService("node.zero-os", nodeID); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
