package node

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetNodeJob is the handler for GET /nodes/{nodeid}/job/{jobid}
// Get the details of a submitted job
func (api *NodeAPI) GetNodeJob(w http.ResponseWriter, r *http.Request) {
	var respBody JobResult
	vars := mux.Vars(r)
	jobID := client.JobId(vars["jobid"])
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	core := client.Core(cl)

	// Check first if the job is running and return
	if process, _ := core.Job(jobID); process != nil {
		respBody = JobResult{
			Id:        process.Command.ID,
			Name:      EnumJobResultName(process.Command.Command),
			StartTime: process.StartTime,
			State:     EnumJobResultStaterunning,
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(&respBody)
		return
	}

	// Check if the job has finished
	if process, _ := cl.ResultNonBlock(jobID); process != nil {
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
		json.NewEncoder(w).Encode(&respBody)
		return
	}

	w.WriteHeader(http.StatusNotFound)
}
