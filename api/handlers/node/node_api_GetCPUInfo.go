package node

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetCPUInfo is the handler for GET /node/{nodeid}/cpu
// Get detailed information of all CPUs in the node
func (api *NodeAPI) GetCPUInfo(w http.ResponseWriter, r *http.Request) {
	cl, err := api.client.GetNodeConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	info := client.Info(cl)
	result, err := info.CPU()
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting cpu info")
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

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
