package node

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetNodeMounts is the handler for GET /nodes/{nodeid}/mounts
// Get detailed information of the mountpoints of the node
func (api *NodeAPI) GetNodeMounts(w http.ResponseWriter, r *http.Request) {
	cl, err := api.client.GetNodeConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	info := client.Info(cl)
	result, err := info.Disk()
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting disk info from node")
		return
	}

	respBody := []NodeMount{}
	for _, mountPoint := range result {
		mount := NodeMount{
			MountPoint: mountPoint.Mountpoint,
			FsType:     mountPoint.Fstype,
			Device:     mountPoint.Device,
			Opts:       mountPoint.Opts,
		}
		respBody = append(respBody, mount)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
