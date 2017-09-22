package node

import (
	"encoding/json"
	"fmt"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ListZerotier is the handler for GET /nodes/{nodeid}/zerotiers
// List running Zerotier networks
func (api *NodeAPI) ListZerotier(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)

	nodeID := mux.Vars(r)["nodeid"]
	// Only zerotiers with the node from the request as parent
	// queryParams := map[string]interface{}{
	// 	"fields": "nwid,status,type",
	// 	"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
	// }

	// services, res, err := aysClient.Ays.ListServicesByRole("zerotier", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, res, w, "listing zerotiers") {
	// 	return
	// }
	services, err := api.client.ListServices("zerotier", ays.ListServiceOpt{
		Parent: fmt.Sprintf("node.zero-os!%s", nodeID),
		Fields: []string{"nwid", "status", "type"},
	})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	respBody := make([]ZerotierListItem, len(services))
	for i, serv := range services {
		var data ZerotierListItem
		if err := json.Unmarshal(serv.Data, &data); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		data.Name = serv.Name
		respBody[i] = data
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
