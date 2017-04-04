package node

import (
	"encoding/json"
	"net/http"
)

// CreateFilesystem is the handler for POST /node/{nodeid}/storagepool/{storagepoolname}/filesystem
// Create a new filesystem
func (api NodeAPI) CreateFilesystem(w http.ResponseWriter, r *http.Request) {
	var reqBody FilesystemCreate

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
