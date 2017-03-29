package main

import (
	"net/http"
)

// KillNodeJob is the handler for DELETE /node/{nodeid}/job/{jobid}
// Kills the job
func (api NodeAPI) KillNodeJob(w http.ResponseWriter, r *http.Request) {
}
