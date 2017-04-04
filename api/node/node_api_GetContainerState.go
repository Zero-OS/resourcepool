package node

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/g8os/grid/api/tools"
)

// GetContainerState is the handler for GET /node/{nodeid}/container/{containerid}/state
// The aggregated consumption of container + all processes (cpu, memory, etc...)
func (api NodeAPI) GetContainerState(w http.ResponseWriter, r *http.Request) {
	container, err := tools.GetContainerConnection(r)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(container)
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
