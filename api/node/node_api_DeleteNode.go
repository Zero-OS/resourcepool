package node

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteNode is the handler for DELETE /nodes/{nodeid}
// Delete Node
func (api *NodeAPI) DeleteNode(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	// return if node doesnt exist
	exists, err := aysClient.ServiceExists("node.zero-os", nodeID, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to check if node exists")
		return
	}
	if !exists {
		w.WriteHeader(http.StatusNoContent)
		return
	}

	query := map[string]interface{}{
		"consume": fmt.Sprintf("node!%s", nodeID),
	}
	services, resp, err := aysClient.Ays.ListServicesByRole("storagecluster", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, resp, w, "listing storageclusters") {
		return
	}

	if len(services) > 0 {
		err = fmt.Errorf("Deleting a node that consume storage clusters is not allowed")
		tools.WriteError(w, http.StatusBadRequest, err, "")
	}

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
