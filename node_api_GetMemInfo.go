package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"net/http"
)

// GetMemInfo is the handler for GET /node/{nodeid}/mem
// Get detailed information about the memory in the node
func (api NodeAPI) GetMemInfo(w http.ResponseWriter, r *http.Request) {
	cl := GetConnection(r)
	info := client.Info(cl)
	result, err := info.Mem()

	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	var respBody MemInfo
	respBody.Active = int(result.Active)
	respBody.Available = int(result.Available)
	respBody.Buffers = int(result.Buffers)
	respBody.Cached = int(result.Cached)
	respBody.Free = int(result.Free)
	respBody.Inactive = int(result.Inactive)
	respBody.Total = int(result.Total)
	respBody.Used = int(result.Used)
	respBody.UsedPercent = result.UsedPercent
	respBody.Wired = int(result.Wired)

	w.Header().Set("content-type", "application/json")
	json.NewEncoder(w).Encode(&respBody)
}
