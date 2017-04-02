package main

import (
	"encoding/json"
	"net/http"
	"strconv"

	client "github.com/g8os/go-client"
	"github.com/gorilla/mux"
)

// GetContainerState is the handler for GET /node/{nodeid}/container/{containerid}/state
// The aggregated consumption of container + all processes (cpu, memory, etc...)
func (api NodeAPI) GetContainerState(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	containerID := vars["containerid"]
	cID, err := strconv.Atoi(containerID)
	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	cl := GetConnection(r)
	contMgr := client.Container(cl)
	container := contMgr.Client(cID)
	core := client.Core(container)
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
