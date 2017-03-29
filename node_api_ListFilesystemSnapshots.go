package main

import (
	"encoding/json"
	"net/http"
)

// ListFilesystemSnapshots is the handler for GET /node/{nodeid}/storagepool/{storagepoolname}/filesystem/{filesystemname}/snapshot
// List snapshots of this filesystem
func (api NodeAPI) ListFilesystemSnapshots(w http.ResponseWriter, r *http.Request) {
	var respBody []string
	json.NewEncoder(w).Encode(&respBody)
}
