package node

import (
	"encoding/json"
	"net/http"
)

// GetContainerCPUInfo is the handler for GET /nodes/{nodeid}/containers/{containername}/cpus
// Get detailed information of all CPUs in the container
func (api NodeAPI) GetContainerCPUInfo(w http.ResponseWriter, r *http.Request) {
	var respBody []CPUInfo
	json.NewEncoder(w).Encode(&respBody)
}
