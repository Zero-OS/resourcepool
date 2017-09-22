package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListStoragePools is the handler for GET /node/{nodeid}/storagepool
// List storage pools present in the node
func (api *NodeAPI) ListStoragePools(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeid),
		"fields": "status,freeCapacity",
	}
	services, _, err := aysClient.Ays.ListServicesByRole("storagepool", api.AysRepo, nil, queryParams)
	if err != nil {
		errmsg := "Error listing storagepool services"
		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	type schema struct {
		Status       string `json:"status"`
		FreeCapacity uint64 `json:"freeCapacity"`
	}

	var respBody = make([]StoragePoolListItem, len(services), len(services))

	for i, service := range services {

		data := schema{}
		if err := json.Unmarshal(service.Data, &data); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		respBody[i] = StoragePoolListItem{
			Status:   EnumStoragePoolListItemStatus(data.Status),
			Capacity: data.FreeCapacity,
			Name:     service.Name,
		}
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
