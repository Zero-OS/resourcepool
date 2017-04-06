package node

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/go-client"
	"github.com/g8os/grid/api/tools"
)

// GetNodeState is the handler for GET /node/{nodeid}/state
// The aggregated consumption of node + all processes (cpu, memory, etc...)
func (api NodeAPI) GetNodeState(w http.ResponseWriter, r *http.Request) {
	cl := tools.GetConnection(r)
	core := client.Core(cl)
	stats, err := core.State()

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	respBody := CoreStateResult{
		Cpu:  stats.CPU,
		Rss:  stats.RSS,
		Vms:  stats.VMS,
		Swap: stats.Swap,
	}
	json.NewEncoder(w).Encode(&respBody)
}
