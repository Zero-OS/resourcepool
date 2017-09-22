package node

import (
	"encoding/json"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetContainer is the handler for GET /nodes/{nodeid}/containers/{containername}
// Get Container
func (api *NodeAPI) GetContainer(w http.ResponseWriter, r *http.Request) {

	vars := mux.Vars(r)
	containername := vars["containername"]
	id, err := api.client.GetContainerID(r, containername)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to get container id")
		return
	}

	service, err := api.client.GetService("container", containername)
	if err != nil {
		api.client.HandlerError(err)
		return
	}

	var respBody Container
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}
	respBody.Id = id

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
