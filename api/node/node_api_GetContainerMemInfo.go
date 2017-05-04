package node

import (
	"encoding/json"
	"net/http"
)

// GetContainerMemInfo is the handler for GET /nodes/{nodeid}/containers/{containername}/mem
// Get detailed information about the memory in the container
func (api NodeAPI) GetContainerMemInfo(w http.ResponseWriter, r *http.Request) {
	var respBody MemInfo
	json.NewEncoder(w).Encode(&respBody)
}
