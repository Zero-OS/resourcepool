package main

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/go-client"
	"github.com/gorilla/mux"
)

// GetNodeJob is the handler for GET /node/{nodeid}/job/{jobid}
// Get the details of a submitted job
func (api NodeAPI) GetNodeJob(w http.ResponseWriter, r *http.Request) {
	var respBody JobResult
	vars := mux.Vars(r)
	jobID := vars["jobid"]
	job := client.Job(jobID)
	cl := GetConnection(r)
	core := client.Core(cl)

	// Check first if the job is running and return
	if process, _ := core.Process(job); process != nil {
		respBody = JobResult{
			Id:        process.Command.ID,
			Name:      EnumJobResultName(process.Command.Command),
			StartTime: process.StartTime,
			State:     EnumJobResultStaterunning,
		}
		w.Header().Set("content-type", "application/json")
		json.NewEncoder(w).Encode(&respBody)
		return
	}

	// Check if the job has finished
	if process, _ := cl.ResultNonBlock(client.Job(jobID)); process != nil {
		respBody = JobResult{
			Data:      process.Data,
			Id:        process.ID,
			Level:     process.Level,
			Name:      EnumJobResultName(process.Command),
			StartTime: process.StartTime,
			Stderr:    process.Streams.Stderr(),
			Stdout:    process.Streams.Stdout(),
			State:     EnumJobResultState(process.State),
		}
		w.Header().Set("content-type", "application/json")
		json.NewEncoder(w).Encode(&respBody)
		return
	}

	w.WriteHeader(http.StatusNotFound)
}
