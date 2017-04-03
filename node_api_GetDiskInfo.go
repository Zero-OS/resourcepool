package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"net/http"
)

// GetDiskInfo is the handler for GET /node/{nodeid}/disk
// Get detailed information of all the disks in the node
func (api NodeAPI) GetDiskInfo(w http.ResponseWriter, r *http.Request) {
	cl := GetConnection(r)
	info := client.Info(cl)
	result, err := info.Disk()
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	var respBody []DiskInfo
	for _, disk := range result {
		var info DiskInfo
		info.Device = disk.Device
		info.Fstype = disk.Fstype
		info.Mountpoint = disk.Mountpoint
		info.Opts = disk.Opts
		respBody = append(respBody, info)
	}

	w.Header().Set("content-type", "application/json")
	json.NewEncoder(w).Encode(&respBody)
}
