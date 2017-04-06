package node

import (
	"encoding/json"
	"net/http"
	"sync"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/mux"

	"fmt"

	"github.com/g8os/grid/api/tools"
)

// ListBridges is the handler for GET /node/{nodeid}/bridge
// List bridges
func (api NodeAPI) ListBridges(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

	queryParams := map[string]interface{}{"parent": fmt.Sprintf("node.g8os!%s", nodeid)}
	services, resp, err := api.AysAPI.Ays.ListServicesByRole("bridge", api.AysRepo, nil, queryParams)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	if resp.StatusCode != http.StatusOK {
		w.WriteHeader(resp.StatusCode)
		return
	}

	wg := sync.WaitGroup{}
	var respBody = make([]Bridge, 0, len(services))
	wg.Add(len(services))

	for _, service := range services {
		go func(name, role string) {
			defer wg.Done()

			srv, resp, err := api.AysAPI.Ays.GetServiceByName(name, role, api.AysRepo, nil, nil)
			if err != nil {
				log.Errorf("Error in listing bridges: %+v\n", err)
				return
			}

			if resp.StatusCode != http.StatusOK {
				log.Errorf("Error in listing bridges: %+v\n", err)
				return
			}

			var bridge Bridge
			if err := json.Unmarshal(srv.Data, &bridge); err != nil {
				log.Errorf("Error in listing bridges: %+v\n", err)
				return
			}
			bridge.Name = srv.Name

			respBody = append(respBody, bridge)
		}(service.Name, service.Role)
	}

	wg.Wait()

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if respBody == nil {
		respBody = []Bridge{}
	}
	json.NewEncoder(w).Encode(&respBody)
}
