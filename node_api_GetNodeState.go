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
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	respBody := CoreStateResult{
		Cpu:  stats.CPU,
		Rss:  int64(stats.RSS),
		Vms:  int64(stats.VMS),
		Swap: int64(stats.Swap),
	}
	json.NewEncoder(w).Encode(&respBody)
}
