package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListGateways is the handler for GET /nodes/{nodeid}/gws
// List running gateways
func (api *NodeAPI) ListGateways(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	// query := map[string]interface{}{
	// 	"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
	// }
	// services, res, err := aysClient.Ays.ListServicesByRole("gateway", api.AysRepo, nil, query)
	// if !tools.HandleAYSResponse(err, res, w, "listing gateways") {
	// 	return
	// }

	services, err := api.client.ListServices("gateway", ays.ListServiceOpt{
		Parent: fmt.Sprintf("node.zero-os!%s", nodeid),
	})
	if err != nil {
		handlers.HandleError(w, err)
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
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
			return
		}
		data.Name = service.Name
		respBody[i] = data
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
