package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// ListGateways is the handler for GET /nodes/{nodeid}/gws
// List running gateways
func (api NodeAPI) ListGateways(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	query := map[string]interface{}{
		"parent": fmt.Sprintf("node.g8os!%s", nodeID),
	}
	services, res, err := api.AysAPI.Ays.ListServicesByRole("gateway", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, res, w, "listing gatways") {
		return
	}

	var respBody = make([]GWCreate, len(services))
	for i, serviceData := range services {
		service, res, err := api.AysAPI.Ays.GetServiceByName(serviceData.Name, serviceData.Role, api.AysRepo, nil, nil)
		if !tools.HandleAYSResponse(err, res, w, "listing gatways") {
			return
		}
		var data GWCreate
		if err := json.Unmarshal(service.Data, &data); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err)
			return
		}
		data.Name = service.Name
		respBody[i] = data
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
