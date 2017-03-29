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
	vars := mux.Vars(r)
	jobID := vars["jobid"]
	cl := GetConnection(r)
	result, err := cl.ResultNonBlock(client.Job(jobID))

	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	if result == nil {
		w.WriteHeader(http.StatusNotFound)
		return
	}

	respBody := JobResult{
		Data:      result.Data,
		Id:        result.ID,
		Level:     result.Level,
		Name:      EnumJobResultName(result.Command),
		StartTime: result.StartTime,
		Stderr:    result.Streams.Stderr(),
		Stdout:    result.Streams.Stdout(),
		State:     EnumJobResultState(result.State),
	}

	w.Header().Set("content-type", "application/json")
	json.NewEncoder(w).Encode(&respBody)
}
