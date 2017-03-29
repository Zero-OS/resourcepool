package main

import (
	"net/http"
)

// KillContainerJob is the handler for DELETE /node/{nodeid}/container/{containerid}/job/{jobid}
// Kills the job
func (api NodeAPI) KillContainerJob(w http.ResponseWriter, r *http.Request) {
}
