package main

import (
	"encoding/json"
	"net/http"
)

// GetClusterInfo is the handler for GET /storagecluster/{label}
// Get full Information about specific cluster
func (api StorageclusterAPI) GetClusterInfo(w http.ResponseWriter, r *http.Request) {
	var respBody Cluster
	json.NewEncoder(w).Encode(&respBody)
}
