package node

import (
	"encoding/json"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetContainer is the handler for GET /nodes/{nodeid}/containers/{containername}
// Get Container
func (api *NodeAPI) GetContainer(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	nodeClient, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to get node connection")
		return
	}
	vars := mux.Vars(r)
	containername := vars["containername"]
	id, _ := tools.GetContainerId(r, api, nodeClient, containername)
	service, res, err := aysClient.Ays.GetServiceByName(containername, "container", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
		return
	}

	var respBody Container
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}
	respBody.Id = id

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
