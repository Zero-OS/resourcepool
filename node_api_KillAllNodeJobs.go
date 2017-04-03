package main

import (
	"net/http"

	"github.com/g8os/go-client"
)

// KillAllNodeJobs is the handler for DELETE /node/{nodeid}/job
// Kills all running jobs
func (api NodeAPI) KillAllNodeJobs(w http.ResponseWriter, r *http.Request) {
	cl := GetConnection(r)
	core := client.Core(cl)

	if err := core.KillAll(); err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
