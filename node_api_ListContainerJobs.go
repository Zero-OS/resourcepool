package main

import (
	"encoding/json"
	"net/http"
	"strconv"

	client "github.com/g8os/go-client"
	"github.com/gorilla/mux"
)

// ListContainerJobs is the handler for GET /node/{nodeid}/container/{containerid}/job
// List running jobs on the container
func (api NodeAPI) ListContainerJobs(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
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
	processes, err := core.Processes()

	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}
	var respBody []JobListItem
	for _, ps := range processes {
		var job JobListItem

		job.Id = ps.Command.ID
		job.StartTime = ps.StartTime
		respBody = append(respBody, job)
	}
	json.NewEncoder(w).Encode(&respBody)
}
