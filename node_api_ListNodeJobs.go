package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"net/http"
)

// ListNodeJobs is the handler for GET /node/{nodeid}/job
// List running jobs
func (api NodeAPI) ListNodeJobs(w http.ResponseWriter, r *http.Request) {
	cl := GetConnection(r)
	core := client.Core(cl)
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
