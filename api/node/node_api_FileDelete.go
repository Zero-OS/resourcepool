package node

import (
	"encoding/json"
	"net/http"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// FileDelete is the handler for DELETE /nodes/{nodeid}/container/{containername}/filesystem
// Delete file from container
func (api *NodeAPI) FileDelete(w http.ResponseWriter, r *http.Request) {

	var reqBody DeleteFile

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]
	containerName := vars["containername"]

	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	// return if node doesnt exist
	exists, err := aysClient.ServiceExists("node.zero-os", nodeID, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to check if node exists")
		return
	}
	if !exists {
		w.WriteHeader(http.StatusNoContent)
		return
	}
	// return if container doesnt exist
	exists, err = aysClient.ServiceExists("container", containerName, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to check if container exists")
		return
	}
	if !exists {
		w.WriteHeader(http.StatusNoContent)
		return
	}

	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
	}

	fs := client.Filesystem(container)
	res, err := fs.Exists(reqBody.Path)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking file exists on container")
		return
	}
	if res != true {
		w.WriteHeader(http.StatusNoContent)
		return
	}

	if err := fs.Remove(reqBody.Path); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error removing file from container")
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
