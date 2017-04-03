package main

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
)

// GetContainerState is the handler for GET /node/{nodeid}/container/{containerid}/state
// The aggregated consumption of container + all processes (cpu, memory, etc...)
func (api NodeAPI) GetContainerState(w http.ResponseWriter, r *http.Request) {
	container, err := GetContainerConnection(r)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(container)
	stats, err := core.State()
	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
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
