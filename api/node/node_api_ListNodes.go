package node

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/grid/api/tools"
)

// ListNodes is the handler for GET /nodes
// List Nodes
func (api NodeAPI) ListNodes(w http.ResponseWriter, r *http.Request) {

	queryParams := map[string]interface{}{
		"fields": "hostname,status,id",
	}
	services, res, err := api.AysAPI.Ays.ListServicesByRole("node", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "listing nodes") {
		return
	}

	var respBody = make([]Node, len(services))
	for i, service := range services {
		var node Node
		if err := json.Unmarshal(service.Data, &node); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err)
			return
		}
		node.Id = service.Name

		respBody[i] = node
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
