package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"net/http"
)

// GetNodeOSInfo is the handler for GET /node/{nodeid}/info
// Get detailed information of the os of the node
func (api NodeAPI) GetNodeOSInfo(w http.ResponseWriter, r *http.Request) {
	cl := GetConnection(r)
	info := client.Info(cl)
	os, err := info.OS()

	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
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
