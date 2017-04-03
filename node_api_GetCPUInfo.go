package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"net/http"
)

// GetCPUInfo is the handler for GET /node/{nodeid}/cpu
// Get detailed information of all CPUs in the node
func (api NodeAPI) GetCPUInfo(w http.ResponseWriter, r *http.Request) {
	cl := GetConnection(r)
	info := client.Info(cl)
	result, err := info.CPU()
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	var respBody []CPUInfo

	for _, cpu := range result {
		var info CPUInfo
		info.CacheSize = cpu.CacheSize
		info.Cores = cpu.Cores
		info.Family = cpu.Family
		info.Flags = cpu.Flags
		info.Mhz = cpu.Mhz

		respBody = append(respBody, info)
	}

	w.Header().Set("content-type", "application/json")
	json.NewEncoder(w).Encode(&respBody)
}
