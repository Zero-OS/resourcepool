package main

import (
	"net/http"

	client "github.com/g8os/go-client"
)

// KillAllContainerJobs is the handler for DELETE /node/{nodeid}/container/{containerid}/job
// Kills all running jobs on the container
func (api NodeAPI) KillAllContainerJobs(w http.ResponseWriter, r *http.Request) {
	container, err := GetContainerConnection(r)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(container)

	if err := core.KillAll(); err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
