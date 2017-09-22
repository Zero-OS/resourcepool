package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetGWForwards is the handler for GET /nodes/{nodeid}/gws/{gwname}/firewall/forwards
// Get list for IPv4 Forwards
func (api *NodeAPI) GetGWForwards(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeId := vars["nodeid"]

	// queryParams := map[string]interface{}{
	// 	"parent": fmt.Sprintf("node.zero-os!%s", nodeId),
	// 	"fields": "portforwards",
	// }

	// service, res, err := aysClient.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
	// 	return
	// }

	services, err := api.client.ListServices("gateway", ays.ListServiceOpt{
		Parent: fmt.Sprintf("node.zero-os!%s", nodeId),
		Fields: []string{"portforwards"},
	})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	var respBody struct {
		PortForwards []PortForward `json:"portforwards"`
	}

	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s' data", gateway)
		httperror.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(respBody.PortForwards)
}
