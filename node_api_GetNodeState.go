package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"net/http"
)

// GetNodeState is the handler for GET /node/{nodeid}/state
// The aggregated consumption of node + all processes (cpu, memory, etc...)
func (api NodeAPI) GetNodeState(w http.ResponseWriter, r *http.Request) {
	cl := GetConnection(r)
	core := client.Core(cl)
	stats, err := core.State()

	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
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
