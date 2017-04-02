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
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	respBody := OSInfo{
		BootTime:             int64(os.BootTime),
		Hostname:             os.Hostname,
		Os:                   os.OS,
		Platform:             os.Platform,
		PlatformFamily:       os.PlatformFamily,
		PlatformVersion:      os.PlatformVersion,
		Procs:                int64(os.Procs),
		Uptime:               int64(os.Uptime),
		VirtualizationRole:   os.VirtualizationRole,
		VirtualizationSystem: os.VirtualizationSystem,
	}
	json.NewEncoder(w).Encode(&respBody)
}
