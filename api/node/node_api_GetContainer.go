package node

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetContainer is the handler for GET /nodes/{nodeid}/containers/{containername}
// Get Container
func (api NodeAPI) GetContainer(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	containername := vars["containername"]
	service, res, err := api.AysAPI.Ays.GetServiceByName(containername, "container", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
		return
	}

	var respBody Container
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
