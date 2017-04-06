package node

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/go-client"
	"github.com/g8os/grid/api/tools"
)

// ListNodeJobs is the handler for GET /node/{nodeid}/job
// List running jobs
func (api NodeAPI) ListNodeJobs(w http.ResponseWriter, r *http.Request) {
	cl := tools.GetConnection(r)
	core := client.Core(cl)
	processes, err := core.Processes()

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
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
