package node

import (
	"encoding/json"
	"net/http"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetContainerState is the handler for GET /nodes/{nodeid}/container/{containername}/state
// The aggregated consumption of container + all processes (cpu, memory, etc...)
func (api *NodeAPI) GetContainerState(w http.ResponseWriter, r *http.Request) {
	// container, err := tools.GetContainerConnection(r, api)
	container, err := api.client.GetContainerConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	core := client.Core(container)
	stats, err := core.State()
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting state of container")
		return
	}

	respBody := CoreStateResult{
		Cpu:  stats.CPU,
		Rss:  stats.RSS,
		Vms:  stats.VMS,
		Swap: stats.Swap,
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
