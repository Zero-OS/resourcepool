package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	str "strings"

	"github.com/gorilla/mux"
	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// StartContainerProcess is the handler for POST /nodes/{nodeid}/containers/{containername}/jobs
// Start a new process in this container
func (api *NodeAPI) StartContainerJob(w http.ResponseWriter, r *http.Request) {
	var reqBody CoreSystem
	env := map[string]string{}

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	for _, item := range reqBody.Environment {
		items := str.Split(item, "=")
		env[items[0]] = items[1]
	}

	containerClient, err := api.GetContainerConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	core := client.Core(containerClient)

	jobID, err := core.SystemArgs(reqBody.Name, reqBody.Args, env, reqBody.Pwd, reqBody.Stdin)

	vars := mux.Vars(r)
	nodeID := vars["nodeid"]
	containername := vars["containername"]
	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/containers/%s/jobs/%s", nodeID, containername, jobID))
	w.WriteHeader(http.StatusAccepted)
}
