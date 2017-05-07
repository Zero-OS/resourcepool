package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// ListStoragePools is the handler for GET /node/{nodeid}/storagepool
// List storage pools present in the node
func (api NodeAPI) ListStoragePools(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.g8os!%s", nodeid),
		"fields": "status,freeCapacity",
	}
	services, _, err := api.AysAPI.Ays.ListServicesByRole("storagepool", api.AysRepo, nil, queryParams)
	if err != nil {
		log.Errorf("Error listing storagepool services : %+v", err)
		tools.WriteError(w, http.StatusInternalServerError, err)
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
			tools.WriteError(w, http.StatusInternalServerError, err)
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
