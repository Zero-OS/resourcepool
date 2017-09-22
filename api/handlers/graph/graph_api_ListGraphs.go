package graph

import (
	"encoding/json"
	"fmt"
	"sync"

	"github.com/zero-os/0-orchestrator/api/ays"
	client "github.com/zero-os/0-orchestrator/api/ays/ays-client"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ListGraphs is the handler for GET /graphs
// List Graphs
func (api *GraphAPI) ListGraphs(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	// queryParams := map[string]interface{}{
	// 	"fields": "node,port",
	// }
	graphServices, err := api.client.ListServices("grafana", ays.ListServiceOpt{
		Fields: []string{"node", "port"},
	})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}

	var wg sync.WaitGroup
	var respBody = make([]Graph, len(graphServices))

	wg.Add(len(graphServices))

	for i, graphService := range graphServices {
		go func(graphService *client.ServiceData, i int) {
			defer wg.Done()
			node, graph, err := api.getNodeOfGraph(graphService)
			if err != nil {
				if aysErr, ok := err.(*ays.Error); ok {
					aysErr.Handle(w, http.StatusInternalServerError)
					return
				}
				httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
			}

			respBody[i].Id = graphService.Name
			if graph.URL != "" {
				respBody[i].URL = graph.URL
			} else {
				respBody[i].URL = fmt.Sprintf("http://%s:%d", node.RedisAddr, graph.Port)
			}

		}(graphService, i)
		// if err := json.Unmarshal(service.Data, &graph); err != nil {
		// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		// 	return
		// }
		// nodeQueryParams := map[string]interface{}{
		// 	"fields": "redisAddr",
		// }
		// nodeService, res, err := aysClient.Ays.GetServiceByName(graph.Node, "node.zero-os", api.AysRepo, nil, nodeQueryParams)
		// if !tools.HandleAYSResponse(err, res, w, "getting node for graph") {
		// 	return
		// }
		// var node NodeService
		// if err := json.Unmarshal(nodeService.Data, &node); err != nil {
		// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		// 	return
		// }
	}

	wg.Wait()

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}

func (api *GraphAPI) getNodeOfGraph(graphService *client.ServiceData) (*NodeService, *GraphService, error) {
	graph := &GraphService{}
	if err := json.Unmarshal(graphService.Data, graph); err != nil {
		return nil, nil, fmt.Errorf("Error unmrshaling ays response: %v", err)
	}

	nodeService, err := api.client.GetService("node.zero-os", graph.Node, "", []string{"redisAddr"})
	if err != nil {
		return nil, nil, err
	}

	node := &NodeService{}
	if err := json.Unmarshal(nodeService.Data, &node); err != nil {
		return nil, nil, fmt.Errorf("Error unmrshaling ays response: %v", err)
	}

	return node, graph, nil
}
