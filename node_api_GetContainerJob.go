package main

import (
	"encoding/json"
	"net/http"
	"strconv"

	client "github.com/g8os/go-client"
	"github.com/gorilla/mux"
)

// GetContainerJob is the handler for GET /node/{nodeid}/container/{containerid}/job/{jobid}
// Get details of a submitted job on the container
func (api NodeAPI) GetContainerJob(w http.ResponseWriter, r *http.Request) {
	var respBody JobResult
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

	// Check first if the job is running and return
	if process, _ := core.Process(jobID); process != nil {
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
	if process, _ := container.ResultNonBlock(jobID); process != nil {
		if int(process.Container) != cID {
			w.WriteHeader(http.StatusNotFound)
			return
		}

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
