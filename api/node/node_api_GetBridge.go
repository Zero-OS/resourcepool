package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/mux"

	"github.com/g8os/resourcepool/api/tools"
)

// GetBridge is the handler for GET /nodes/{nodeid}/bridges/{bridgeid}
// Get bridge details
func (api NodeAPI) GetBridge(w http.ResponseWriter, r *http.Request) {
	var respBody Bridge

	vars := mux.Vars(r)
	bridge := vars["bridgeid"]
	srv, resp, err := api.AysAPI.Ays.GetServiceByName(bridge, "bridge", api.AysRepo, nil, nil)

	if err != nil {
		log.Errorf("Error in getting bridge service %s : %+v", bridge, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if resp.StatusCode == http.StatusNotFound {
		tools.WriteError(w, http.StatusNotFound, fmt.Errorf("Bridge %s does not exist", bridge))
		return
	}

	if err := json.Unmarshal(srv.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	respBody.Name = srv.Name

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(&respBody); err != nil {
		log.Errorf("Error in encoding response: %+v", err)
	}
}
