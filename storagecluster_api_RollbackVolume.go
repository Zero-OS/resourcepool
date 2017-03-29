package main

import (
	"encoding/json"
	"net/http"
)

// RollbackVolume is the handler for POST /storagecluster/{label}/volumes/{volumeid}/rollback
// Rollback a volume to a previous state
func (api StorageclusterAPI) RollbackVolume(w http.ResponseWriter, r *http.Request) {
	var reqBody VolumeRollback

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
