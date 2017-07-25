package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetGraph is the handler for GET /graphs/{graphid}
// Get Graph
func (api NodeAPI) GetGraph(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	graphId := vars["graphid"]
	queryParams := map[string]interface{}{
		"fields": "node,port",
	}
	service, res, err := aysClient.Ays.GetServiceByName(graphId, "grafana", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "get graph") {
		return
	}

	var respBody Graph
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

	if graph.URL != "" {
		respBody.URL = graph.URL
	} else {
		respBody.URL = fmt.Sprintf("http://%s:%d", node.RedisAddr, graph.Port)
	}
	respBody.Id = service.Name

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
