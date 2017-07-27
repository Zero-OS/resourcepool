package graph

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListGraphs is the handler for GET /graphs
// List Graphs
func (api GraphAPI) ListGraphs(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	queryParams := map[string]interface{}{
		"fields": "node,port",
	}
	services, res, err := aysClient.Ays.ListServicesByRole("grafana", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "listing graphs") {
		return
	}

	var respBody = make([]Graph, len(services))
	for i, service := range services {
		var graph GraphService
		if err := json.Unmarshal(service.Data, &graph); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}
		nodeQueryParams := map[string]interface{}{
			"fields": "redisAddr",
		}
		nodeService, res, err := aysClient.Ays.GetServiceByName(graph.Node, "node.zero-os", api.AysRepo, nil, nodeQueryParams)
		if !tools.HandleAYSResponse(err, res, w, "getting node for graph") {
			return
		}
		var node NodeService
		if err := json.Unmarshal(nodeService.Data, &node); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		respBody[i].Id = service.Name
		if graph.URL != "" {
			respBody[i].URL = graph.URL
		} else {
			respBody[i].URL = fmt.Sprintf("http://%s:%d", node.RedisAddr, graph.Port)
		}
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
