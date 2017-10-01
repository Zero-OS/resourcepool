package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListGateways is the handler for GET /nodes/{nodeid}/gws
// List running gateways
func (api *NodeAPI) ListGateways(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	query := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
	}
	services, res, err := aysClient.Ays.ListServicesByRole("gateway", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, res, w, "listing gateways") {
		return
	}

	var respBody = make([]ListGW, len(services))
	for i, serviceData := range services {
		service, res, err := aysClient.Ays.GetServiceByName(serviceData.Name, serviceData.Role, api.AysRepo, nil, nil)
		if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
			return
		}
		var data ListGW
		if err := json.Unmarshal(service.Data, &data); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
			return
		}
		data.Name = service.Name
		respBody[i] = data
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
