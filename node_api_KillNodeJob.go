package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"github.com/gorilla/mux"
	"net/http"
)

// KillNodeJob is the handler for DELETE /node/{nodeid}/job/{jobid}
// Kills the job
func (api NodeAPI) KillNodeJob(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := vars["jobid"]
	cl := GetConnection(r)
	core := client.Core(cl)

	if err := core.Kill(client.Job(jobID)); err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
