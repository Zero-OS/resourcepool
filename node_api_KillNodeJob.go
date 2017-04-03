package main

import (
	"net/http"

	"github.com/g8os/go-client"
	"github.com/gorilla/mux"
)

// KillNodeJob is the handler for DELETE /node/{nodeid}/job/{jobid}
// Kills the job
func (api NodeAPI) KillNodeJob(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := vars["jobid"]
	cl := GetConnection(r)
	core := client.Core(cl)

	if err := core.Kill(client.Job(jobID)); err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
