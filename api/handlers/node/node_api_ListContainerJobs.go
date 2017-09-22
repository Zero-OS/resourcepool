package node

import (
	"encoding/json"
	"net/http"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ListContainerJobs is the handler for GET /nodes/{nodeid}/container/{containername}/job
// List running jobs on the container
func (api *NodeAPI) ListContainerJobs(w http.ResponseWriter, r *http.Request) {
	container, err := api.client.GetContainerConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	core := client.Core(container)
	processes, err := core.Jobs()
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting jobs from container")
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
