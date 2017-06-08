package node

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListNodeJobs is the handler for GET /nodes/{nodeid}/job
// List running jobs
func (api NodeAPI) ListNodeJobs(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "")
		return
	}

	core := client.Core(cl)
	processes, err := core.Jobs()

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "")
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
