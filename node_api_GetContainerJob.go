package main

import (
	"encoding/json"
	"net/http"
)

// GetContainerJob is the handler for GET /node/{nodeid}/container/{containerid}/job/{jobid}
// Get details of a submitted job on the container
func (api NodeAPI) GetContainerJob(w http.ResponseWriter, r *http.Request) {
	var respBody JobResult
	json.NewEncoder(w).Encode(&respBody)
}
