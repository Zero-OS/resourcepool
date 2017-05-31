package node

import (
	"encoding/json"
	"net/http"

	client "github.com/zero-os/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// PingContainer is the handler for POST /nodes/{nodeid}/containers/{containername}/ping
// Ping this container
func (api NodeAPI) PingContainer(w http.ResponseWriter, r *http.Request) {
	var respBody bool
	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(container)

	if err := core.Ping(); err != nil {
		respBody = false
	} else {
		respBody = true
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
