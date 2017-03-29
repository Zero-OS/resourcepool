package main

import (
	"encoding/json"
	"net/http"
)

// GetContainerProcess is the handler for GET /node/{nodeid}/container/{containerid}/process/{proccessid}
// Get process details
func (api NodeAPI) GetContainerProcess(w http.ResponseWriter, r *http.Request) {
	var respBody Process
	json.NewEncoder(w).Encode(&respBody)
}
