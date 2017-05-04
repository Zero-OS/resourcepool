package node

import (
	"encoding/json"
	"net/http"
)

// GetContainerDiskInfo is the handler for GET /nodes/{nodeid}/containers/{containername}/disks
// Get detailed information of all the disks in the container
func (api NodeAPI) GetContainerDiskInfo(w http.ResponseWriter, r *http.Request) {
	var respBody []DiskInfo
	json.NewEncoder(w).Encode(&respBody)
}
