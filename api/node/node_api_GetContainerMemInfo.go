package node

import (
	"encoding/json"
	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	"net/http"
)

// GetContainerMemInfo is the handler for GET /nodes/{nodeid}/containers/{containername}/mem
// Get detailed information about the memory in the container
func (api NodeAPI) GetContainerMemInfo(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	info := client.Info(cl)
	result, err := info.Mem()

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error getting memory info from container")
		return
	}

	var respBody MemInfo
	respBody.Active = int(result.Active)
	respBody.Available = int(result.Available)
	respBody.Buffers = int(result.Buffers)
	respBody.Cached = int(result.Cached)
	respBody.Free = int(result.Free)
	respBody.Inactive = int(result.Inactive)
	respBody.Total = int(result.Total)
	respBody.Used = int(result.Used)
	respBody.UsedPercent = result.UsedPercent
	respBody.Wired = int(result.Wired)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
