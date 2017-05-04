package node

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// GetContainerJob is the handler for GET /nodes/{nodeid}/container/{containername}/job/{jobid}
// Get details of a submitted job on the container
func (api NodeAPI) GetContainerJob(w http.ResponseWriter, r *http.Request) {
	var respBody JobResult

	vars := mux.Vars(r)
	jobID := client.JobId(vars["jobid"])

	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(container)

	// Check first if the job is running and return
	if process, _ := core.Job(jobID); process != nil {
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

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	// Check if the job has finished
	if process, _ := container.ResultNonBlock(jobID); process != nil {

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

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		json.NewEncoder(w).Encode(&respBody)
		return
	}

	w.WriteHeader(http.StatusNotFound)
}
