package main

import (
	"encoding/json"
	"net/http"
)

// ListContainerJobs is the handler for GET /node/{nodeid}/container/{containerid}/job
// List running jobs on the container
func (api NodeAPI) ListContainerJobs(w http.ResponseWriter, r *http.Request) {
	var respBody []JobListItem
	json.NewEncoder(w).Encode(&respBody)
}
