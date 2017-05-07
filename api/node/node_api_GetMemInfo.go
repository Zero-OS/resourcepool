package node

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
)

// GetMemInfo is the handler for GET /nodes/{nodeid}/mem
// Get detailed information about the memory in the node
func (api NodeAPI) GetMemInfo(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	info := client.Info(cl)
	result, err := info.Mem()

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
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
