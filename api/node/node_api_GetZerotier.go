package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetZerotier is the handler for GET /nodes/{nodeid}/zerotiers/{zerotierid}
// Get Zerotier network details
func (api *NodeAPI) GetZerotier(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var respBody Zerotier

	vars := mux.Vars(r)
	nodeID := vars["nodeid"]
	zerotierID := vars["zerotierid"]

	srv, res, err := aysClient.Ays.GetServiceByName(fmt.Sprintf("%s_%s", nodeID, zerotierID), "zerotier", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, fmt.Sprintf("getting zerotier %s details", zerotierID)) {
		return
	}

	if err := json.Unmarshal(srv.Data, &respBody); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
