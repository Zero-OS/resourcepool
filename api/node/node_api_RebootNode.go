package node

import (
	"net/http"

	"encoding/json"
	"fmt"
	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

type RebootBP struct {
	ForceReboot bool `json:"forceReboot" yaml:"forceReboot"`
}

// RebootNode is the handler for POST /nodes/{nodeid}/reboot
// Immediately reboot the machine.
func (api *NodeAPI) RebootNode(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	tools.DeleteConnection(r)
	vars := mux.Vars(r)
	nodeId := vars["nodeid"]
	var reqBody NodeReboot

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	blueprint := make(map[string]interface{})
	blueprint[fmt.Sprintf("node.zero-os__%s", nodeId)] =  RebootBP{
		ForceReboot: reqBody.Force,
	}
	blueprint["actions"] = []tools.ActionBlock{{
		Action:  "reboot",
		Actor:   "node.zero-os",
		Service: nodeId,
		Force:   true,
	}}

	_, err := aysClient.ExecuteBlueprint(api.AysRepo, "node", nodeId, "reboot", blueprint)
	if !tools.HandleExecuteBlueprintResponse(err, w, "Error running blueprint for Rebooting node") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
