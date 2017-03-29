package main

import (
	"encoding/json"
	"net/http"
)

// GetNodeOSInfo is the handler for GET /node/{nodeid}/info
// Get detailed information of the os of the node
func (api NodeAPI) GetNodeOSInfo(w http.ResponseWriter, r *http.Request) {
	var respBody OSInfo
	json.NewEncoder(w).Encode(&respBody)
}
