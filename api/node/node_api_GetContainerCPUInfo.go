package node

import (
	"encoding/json"
	"net/http"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetContainerCPUInfo is the handler for GET /nodes/{nodeid}/containers/{containername}/cpus
// Get detailed information of all CPUs in the container
func (api *NodeAPI) GetContainerCPUInfo(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	info := client.Info(cl)
	result, err := info.CPU()
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error getting cpu info for container")
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
