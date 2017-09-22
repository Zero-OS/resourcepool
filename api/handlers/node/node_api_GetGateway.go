package node

import (
	"encoding/json"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetGateway is the handler for GET /nodes/{nodeid}/gws/{gwname}
// Get gateway
func (api *NodeAPI) GetGateway(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var gateway GetGW

	vars := mux.Vars(r)
	gwname := vars["gwname"]
	// service, res, err := aysClient.Ays.GetServiceByName(gwname, "gateway", api.AysRepo, nil, nil)

	// if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
	// 	return
	// }
	service, err := api.client.GetService("gateway", gwname, "", nil)
	if err != nil {
		handler.HandleError(w, err)
		return
	}

	if err := json.Unmarshal(service.Data, &gateway); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&gateway)
}
