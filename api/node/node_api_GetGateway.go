package node

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// GetGateway is the handler for GET /nodes/{nodeid}/gws/{gwname}
// Get gateway
func (api NodeAPI) GetGateway(w http.ResponseWriter, r *http.Request) {
	var gateway GetGW

	vars := mux.Vars(r)
	gwname := vars["gwname"]
	service, res, err := api.AysAPI.Ays.GetServiceByName(gwname, "gateway", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
		return
	}

	if err := json.Unmarshal(service.Data, &gateway); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&gateway)
}
