package main

import (
	"encoding/json"
	"net/http"
)

// CreateNewVolume is the handler for POST /storagecluster/{label}/volumes
// Create a new volume, can be a copy from an existing volume
func (api StorageclusterAPI) CreateNewVolume(w http.ResponseWriter, r *http.Request) {
	var reqBody VolumeCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}
}
