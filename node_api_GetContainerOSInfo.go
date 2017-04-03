package main

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
)

// GetContainerOSInfo is the handler for GET /node/{nodeid}/container/{containerid}/info
// Get detailed information of the container os
func (api NodeAPI) GetContainerOSInfo(w http.ResponseWriter, r *http.Request) {
	container, err := GetContainerConnection(r)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	info := client.Info(container)
	os, err := info.OS()
	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
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
