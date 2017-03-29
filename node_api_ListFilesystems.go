package main

import (
	"encoding/json"
	"net/http"
)

// ListFilesystems is the handler for GET /node/{nodeid}/storagepool/{storagepoolname}/filesystem
// List filesystems
func (api NodeAPI) ListFilesystems(w http.ResponseWriter, r *http.Request) {
	var respBody []string
	json.NewEncoder(w).Encode(&respBody)
}
