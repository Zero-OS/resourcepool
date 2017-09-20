package node

import (
	"encoding/json"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListNodes is the handler for GET /nodes
// List Nodes
func (api *NodeAPI) ListNodes(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	queryParams := map[string]interface{}{
		"fields": "hostname,status,id,redisAddr",
	}
	services, res, err := aysClient.Ays.ListServicesByRole("node.zero-os", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "listing nodes") {
		return
	}

	var respBody = make([]Node, len(services))
	for i, service := range services {
		var node NodeService
		if err := json.Unmarshal(service.Data, &node); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		respBody[i].IPAddress = node.RedisAddr
		respBody[i].Status = node.Status
		respBody[i].Hostname = node.Hostname
		respBody[i].Id = service.Name
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
