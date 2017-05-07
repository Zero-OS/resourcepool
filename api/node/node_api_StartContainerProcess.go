package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	str "strings"

	client "github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// StartContainerProcess is the handler for POST /nodes/{nodeid}/containers/{containername}/processes
// Start a new process in this container
func (api NodeAPI) StartContainerProcess(w http.ResponseWriter, r *http.Request) {
	var reqBody CoreSystem
	var env map[string]string

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}

	for _, item := range reqBody.Environment {
		items := str.Split(item, "=")
		env[items[0]] = items[1]
	}

	containerClient, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
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
