package node

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetNodeOSInfo is the handler for GET /nodes/{nodeid}/info
// Get detailed information of the os of the node
func (api *NodeAPI) GetNodeOSInfo(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	info := client.Info(cl)
	os, err := info.OS()

	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting os info from node")
		return
	}

	respBody := OSInfo{
		BootTime:             os.BootTime,
		Hostname:             os.Hostname,
		Os:                   os.OS,
		Platform:             os.Platform,
		PlatformFamily:       os.PlatformFamily,
		PlatformVersion:      os.PlatformVersion,
		Procs:                os.Procs,
		Uptime:               os.Uptime,
		VirtualizationRole:   os.VirtualizationRole,
		VirtualizationSystem: os.VirtualizationSystem,
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(&respBody)
}
