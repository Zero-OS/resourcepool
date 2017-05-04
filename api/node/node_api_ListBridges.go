package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// ListBridges is the handler for GET /nodes/{nodeid}/bridges
// List bridges
func (api NodeAPI) ListBridges(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.g8os!%s", nodeid),
		"fields": "setting,status",
	}
	services, resp, err := api.AysAPI.Ays.ListServicesByRole("bridge", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, resp, w, "listing bridges") {
		return
	}

	var respBody = make([]Bridge, len(services))
	for i, service := range services {
		bridge := Bridge{
			Name: service.Name,
		}

		if err := json.Unmarshal(service.Data, &bridge); err != nil {
			log.Errorf("Error in listing bridges: %+v\n", err)
			tools.WriteError(w, http.StatusInternalServerError, err)
			return
		}

		respBody[i] = bridge
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
