package main

import (
	"encoding/json"
	"net/http"
)

// GetContainerState is the handler for GET /node/{nodeid}/container/{containerid}/state
// The aggregated consumption of container + all processes (cpu, memory, etc...)
func (api NodeAPI) GetContainerState(w http.ResponseWriter, r *http.Request) {
	var respBody CoreStateResult
	json.NewEncoder(w).Encode(&respBody)
}
