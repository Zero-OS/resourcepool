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

// ListContainers is the handler for GET /nodes/{nodeid}/containers
// List running Containers
func (api *NodeAPI) ListContainers(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	// query := map[string]interface{}{
	// 	"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
	// 	"fields": "flist,hostname,status",
	// }
	// services, res, err := aysClient.Ays.ListServicesByRole("container", api.AysRepo, nil, query)
	// if err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting container services from ays")
	// 	return
	// }
	// if res.StatusCode != http.StatusOK {
	// 	w.WriteHeader(res.StatusCode)
	// 	return
	// }
	services, err := api.client.ListServices("container", ays.ListServiceOpt{
		Parent: fmt.Sprintf("node.zero-os!%s", nodeID),
		Fields: []string{"flist", "hostname", "status"},
	})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	type containerItem struct {
		Flist    string                      `json:"flist" validate:"nonzero"`
		Hostname string                      `json:"hostname" validate:"nonzero"`
		Status   EnumContainerListItemStatus `json:"status" validate:"nonzero"`
	}

	var respBody = make([]ContainerListItem, len(services))
	for i, service := range services {
		var data containerItem
		if err := json.Unmarshal(service.Data, &data); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		container := ContainerListItem{
			Name:     service.Name,
			Flist:    data.Flist,
			Hostname: data.Hostname,
			Status:   data.Status,
		}
		respBody[i] = container
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
