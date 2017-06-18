package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// RebootNode is the handler for POST /nodes/{nodeid}/reboot
// Immediately reboot the machine.
func (api NodeAPI) RebootNode(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	tools.DeleteConnection(r)
	vars := mux.Vars(r)
	nodeId := vars["nodeid"]

	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "reboot",
			Actor:   "node.zero-os",
			Service: nodeId,
			Force:   true,
		}},
	}

	_, err := aysClient.ExecuteBlueprint(api.AysRepo, "node", nodeId, "reboot", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
