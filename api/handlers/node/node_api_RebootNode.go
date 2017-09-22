package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"github.com/gorilla/mux"
)

// RebootNode is the handler for POST /nodes/{nodeid}/reboot
// Immediately reboot the machine.
func (api *NodeAPI) RebootNode(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)

	// invalidate cache
	api.client.DeleteConnection(r)

	// tools.DeleteConnection(r)
	vars := mux.Vars(r)
	nodeId := vars["nodeid"]

	blueprint := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "reboot",
			Actor:   "node.zero-os",
			Service: nodeId,
			Force:   true,
		}},
	}

	blueprintName := ays.BlueprintName("node", nodeId, "reboot")
	if err := api.client.CreateExec(blueprintName, blueprint); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// _, err := aysClient.ExecuteBlueprint(api.AysRepo, "node", nodeId, "reboot", blueprint)
	// if !tools.HandleExecuteBlueprintResponse(err, w, "Error running blueprint for Rebooting node") {
	// 	return
	// }

	w.WriteHeader(http.StatusNoContent)
}
