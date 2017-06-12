package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// RebootNode is the handler for POST /nodes/{nodeid}/reboot
// Immediately reboot the machine.
func (api NodeAPI) RebootNode(w http.ResponseWriter, r *http.Request) {
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

	_, err := tools.ExecuteBlueprint(api.AysRepo, "node", nodeId, "reboot", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
