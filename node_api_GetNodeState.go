package main

import (
	"encoding/json"
	"net/http"
)

// GetNodeState is the handler for GET /node/{nodeid}/state
// The aggregated consumption of node + all processes (cpu, memory, etc...)
func (api NodeAPI) GetNodeState(w http.ResponseWriter, r *http.Request) {
	var respBody CoreStateResult
	json.NewEncoder(w).Encode(&respBody)
}
