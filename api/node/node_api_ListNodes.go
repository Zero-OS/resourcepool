package node

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/grid/api/tools"
)

// ListNodes is the handler for GET /nodes
// List Nodes
func (api NodeAPI) ListNodes(w http.ResponseWriter, r *http.Request) {
	services, res, err := api.AysAPI.Ays.ListServicesByRole("node", api.AysRepo, nil, nil)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	if res.StatusCode != http.StatusOK {
		w.WriteHeader(res.StatusCode)
		return
	}

	var respBody []Node
	for _, service := range services {
		srv, res, err := api.AysAPI.Ays.GetServiceByName(service.Name, "node", api.AysRepo, nil, nil)

		if err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err)
			return
		}

		if res.StatusCode != http.StatusOK {
			w.WriteHeader(res.StatusCode)
			return
		}

		var node Node
		if err := json.Unmarshal(srv.Data, &node); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err)
			return
		}

		node.Id = service.Name
		respBody = append(respBody, node)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
