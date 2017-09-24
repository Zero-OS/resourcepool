package node

import (
	"encoding/json"
	"net/http"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetContainerOSInfo is the handler for GET /nodes/{nodeid}/container/{containername}/info
// Get detailed information of the container os
func (api *NodeAPI) GetContainerOSInfo(w http.ResponseWriter, r *http.Request) {
	// container, err := tools.GetContainerConnection(r, api)
	container, err := api.client.GetContainerConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	info := client.Info(container)
	os, err := info.OS()
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting os info on container")
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
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
