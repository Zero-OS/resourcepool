package node

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/g8os/grid/api/tools"
)

// ListContainerJobs is the handler for GET /node/{nodeid}/container/{containerid}/job
// List running jobs on the container
func (api NodeAPI) ListContainerJobs(w http.ResponseWriter, r *http.Request) {
	container, err := tools.GetContainerConnection(r)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(container)
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
