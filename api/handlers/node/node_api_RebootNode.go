package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
)

// RebootNode is the handler for POST /nodes/{nodeid}/reboot
// Immediately reboot the machine.
func (api *NodeAPI) RebootNode(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	ays.DeleteConnection(r)
	vars := mux.Vars(r)
	nodeId := vars["nodeid"]

	blueprint := map[string]interface{}{
		"actions": []ays.ActionBlock{{
			Action:  "reboot",
			Actor:   "node.zero-os",
			Service: nodeId,
			Force:   true,
		}},
	}

	// _, err := aysClient.ExecuteBlueprint(api.AysRepo, "node", nodeId, "reboot", blueprint)
	// if !tools.HandleExecuteBlueprintResponse(err, w, "Error running blueprint for Rebooting node") {
	// 	return
	// }
	blueprintName := ays.BlueprintName("node", nodeId, "reboot")
	if err := api.client.CreateExec(blueprintName, blueprint); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
