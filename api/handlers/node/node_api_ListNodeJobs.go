package node

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ListNodeJobs is the handler for GET /nodes/{nodeid}/job
// List running jobs
func (api *NodeAPI) ListNodeJobs(w http.ResponseWriter, r *http.Request) {
	cl, err := api.client.GetNodeConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	core := client.Core(cl)
	processes, err := core.Jobs()

	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting jobs from node")
		return
	}
	var respBody []JobListItem
	for _, ps := range processes {
		var job JobListItem

		job.Id = ps.Command.ID
		job.StartTime = ps.StartTime
		respBody = append(respBody, job)
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
