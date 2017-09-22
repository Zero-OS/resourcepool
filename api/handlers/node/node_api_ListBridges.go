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

// ListBridges is the handler for GET /nodes/{nodeid}/bridges
// List bridges
func (api *NodeAPI) ListBridges(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

	// queryParams := map[string]interface{}{
	// 	"parent": fmt.Sprintf("node.zero-os!%s", nodeid),
	// 	"fields": "setting,status",
	// }
	// services, resp, err := aysClient.Ays.ListServicesByRole("bridge", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, resp, w, "listing bridges") {
	// 	return
	// }
	services, err := api.client.ListServices("bridge", ays.ListServiceOpt{
		Parent: fmt.Sprintf("node.zero-os!%s", nodeid),
		Fields: []string{"setting", "status"},
	})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	var respBody = make([]Bridge, len(services))
	for i, service := range services {
		bridge := Bridge{
			Name: service.Name,
		}

		if err := json.Unmarshal(service.Data, &bridge); err != nil {
			errmsg := "Error in listing bridges"
			httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
			return
		}

		respBody[i] = bridge
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
