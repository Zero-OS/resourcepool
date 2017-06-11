package node

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// PingNode is the handler for POST /nodes/{nodeid}/ping
// Ping this node
func (api NodeAPI) PingNode(w http.ResponseWriter, r *http.Request) {
	var respBody bool
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	core := client.Core(cl)

	if err := core.Ping(); err != nil {
		respBody = false
	} else {
		respBody = true
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
