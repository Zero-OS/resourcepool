package node

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
)

// GetNodeMounts is the handler for GET /nodes/{nodeid}/mounts
// Get detailed information of the mountpoints of the node
func (api NodeAPI) GetNodeMounts(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	info := client.Info(cl)
	result, err := info.Disk()
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	respBody := []NodeMount{}
	for _, mountPoint :=  range result {
		mount := NodeMount{
			MountPoint: mountPoint.Mountpoint,
			FsType: mountPoint.Fstype,
			Device: mountPoint.Device,
			Opts: mountPoint.Opts,
		}
		respBody = append(respBody, mount)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
