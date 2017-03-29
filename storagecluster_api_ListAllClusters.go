package main

import (
	"encoding/json"
	"net/http"
)

// ListAllClusters is the handler for GET /storagecluster
// List all running clusters
func (api StorageclusterAPI) ListAllClusters(w http.ResponseWriter, r *http.Request) {
	var respBody []string
	json.NewEncoder(w).Encode(&respBody)
}
