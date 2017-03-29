package main

import (
	"encoding/json"
	"net/http"
)

// CreateSnapshot is the handler for POST /node/{nodeid}/storagepool/{storagepoolname}/filesystem/{filesystemname}/snapshot
// Create a new readonly filesystem of the current state of the volume
func (api NodeAPI) CreateSnapshot(w http.ResponseWriter, r *http.Request) {
	var reqBody string

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}
}
