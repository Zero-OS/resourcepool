package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// ListContainers is the handler for GET /nodes/{nodeid}/containers
// List running Containers
func (api NodeAPI) ListContainers(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	query := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
		"fields": "flist,hostname,status",
	}
	services, res, err := api.AysAPI.Ays.ListServicesByRole("container", api.AysRepo, nil, query)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	if res.StatusCode != http.StatusOK {
		w.WriteHeader(res.StatusCode)
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
			tools.WriteError(w, http.StatusInternalServerError, err)
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
