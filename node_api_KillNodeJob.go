package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"github.com/gorilla/mux"
	"net/http"
	"strconv"
)

// KillNodeJob is the handler for DELETE /node/{nodeid}/job/{jobid}
// Kills the job
func (api NodeAPI) KillNodeJob(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	jobID := client.Job(vars["jobid"])
	containerID := vars["containerid"]

	cID, err := strconv.Atoi(containerID)
	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	cl := GetConnection(r)
	contMgr := client.Container(cl)
	container := contMgr.Client(cID)
	core := client.Core(container)

	if err := core.Kill(jobID); err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
