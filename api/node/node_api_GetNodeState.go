package node

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetNodeState is the handler for GET /nodes/{nodeid}/state
// The aggregated consumption of node + all processes (cpu, memory, etc...)
func (api *NodeAPI) GetNodeState(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	core := client.Core(cl)
	stats, err := core.State()

	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting state of node")
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
