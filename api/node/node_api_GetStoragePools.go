package node

import (
	"encoding/json"
	"net/http"
	"sync"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/grid/api/tools"
)

// GetStoragePools is the handler for GET /node/{nodeid}/storagepool
// List storage pools present in the node
func (api NodeAPI) GetStoragePools(w http.ResponseWriter, r *http.Request) {

	services, _, err := api.AysAPI.Ays.ListServicesByRole("storagepool", api.AysRepo, nil, nil)
	if err != nil {
		log.Errorf("Error listing storagepool services : %+v", err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	// grab all service details concurently
	wg := sync.WaitGroup{}
	var respBody = make([]StoragePoolListItem, 0, len(services))
	wg.Add(len(services))

	for i, service := range services {
		go func(name string, i int) {
			defer wg.Done()

			schema, err := api.getStoragepoolDetail(name)
			if err != nil {
				log.Errorf("Error getting detail for storgepool %s : %+v\n", name, err)
				return
			}

			respBody = append(respBody, StoragePoolListItem{
				Status:   EnumStoragePoolListItemStatus(schema.Status),
				Capacity: schema.FreeCapacity,
				Name:     name,
			})
		}(service.Name, i)
	}

	wg.Wait()

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
