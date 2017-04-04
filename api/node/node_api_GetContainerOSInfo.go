package node

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/g8os/grid/api/tools"
)

// GetContainerOSInfo is the handler for GET /node/{nodeid}/container/{containerid}/info
// Get detailed information of the container os
func (api NodeAPI) GetContainerOSInfo(w http.ResponseWriter, r *http.Request) {
	container, err := tools.GetContainerConnection(r)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	info := client.Info(container)
	os, err := info.OS()
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
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
	json.NewEncoder(w).Encode(&respBody)
}
