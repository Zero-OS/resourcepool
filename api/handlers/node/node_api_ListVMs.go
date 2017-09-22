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

// ListVMs is the handler for GET /node/{nodeid}/vm
// List VMs
func (api *NodeAPI) ListVMs(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)

	// queryParams := map[string]interface{}{
	// 	"fields": "status,id",
	// 	"parent": fmt.Sprintf("node.zero-os!%s", vars["nodeid"]),
	// }
	// services, res, err := aysClient.Ays.ListServicesByRole("vm", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, res, w, "listing vms") {
	// 	return
	// }
	services, err := api.client.ListServices("vm", ays.ListServiceOpt{
		Parent: fmt.Sprintf("node.zero-os!%s", vars["nodeid"]),
		Fields: []string{"status", "id"},
	})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	var respBody = make([]VMListItem, len(services))
	for i, service := range services {
		var vm VMListItem
		if err := json.Unmarshal(service.Data, &vm); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}
		vm.Id = service.Name

		respBody[i] = vm
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
