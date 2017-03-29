package main

import (
	"encoding/json"
	"net/http"
)

// GetContainerOSInfo is the handler for GET /node/{nodeid}/container/{containerid}/info
// Get detailed information of the container os
func (api NodeAPI) GetContainerOSInfo(w http.ResponseWriter, r *http.Request) {
	var respBody OSInfo
	json.NewEncoder(w).Encode(&respBody)
}
