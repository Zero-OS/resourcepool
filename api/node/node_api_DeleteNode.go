package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteNode is the handler for DELETE /nodes/{nodeid}
// Delete Node
func (api *NodeAPI) DeleteNode(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	// execute the uninstall action of the node
	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "uninstall",
			Actor:   "node.zero-os",
			Service: nodeID,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "node.zero-os", nodeID, "uninstall", bp)
	errmsg := "Error executing blueprint for node uninstallation "
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	// Wait for the uninstall job to be finshed before we delete the service
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for node uninstallation")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for node uninstallation")
		}
		return
	}

	res, err := aysClient.Ays.DeleteServiceByName(nodeID, "node.zero-os", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "deleting service") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
