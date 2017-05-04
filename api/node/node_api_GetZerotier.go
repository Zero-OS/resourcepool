package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// GetZerotier is the handler for GET /nodes/{nodeid}/zerotiers/{zerotierid}
// Get Zerotier network details
func (api NodeAPI) GetZerotier(w http.ResponseWriter, r *http.Request) {
	var respBody Zerotier

	vars := mux.Vars(r)
	nodeID := vars["nodeid"]
	zerotierID := vars["zerotierid"]

	srv, res, err := api.AysAPI.Ays.GetServiceByName(fmt.Sprintf("%s_%s", nodeID, zerotierID), "zerotier", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, fmt.Sprintf("getting zerotier %s details", zerotierID)) {
		return
	}

	if err := json.Unmarshal(srv.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
