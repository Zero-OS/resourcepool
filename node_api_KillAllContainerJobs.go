package main

import (
	"net/http"
)

// KillAllContainerJobs is the handler for DELETE /node/{nodeid}/container/{containerid}/job
// Kills all running jobs on the container
func (api NodeAPI) KillAllContainerJobs(w http.ResponseWriter, r *http.Request) {
}
