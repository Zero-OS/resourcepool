package node

import (
	"encoding/json"

	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetBridge is the handler for GET /nodes/{nodeid}/bridges/{bridgeid}
// Get bridge details
func (api *NodeAPI) GetBridge(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)

	var respBody Bridge

	vars := mux.Vars(r)
	bridge := vars["bridgeid"]
	// srv, resp, err := aysClient.Ays.GetServiceByName(bridge, "bridge", api.AysRepo, nil, nil)

	// if !tools.HandleAYSResponse(err, resp, w, "Get bridge by name") {
	// 	return
	// }

	srv, err := api.client.GetService("bridge", bridge, "", []string{"RedisAddr"})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	if err := json.Unmarshal(srv.Data, &respBody); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
		return
	}
	respBody.Name = srv.Name

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	if err := json.NewEncoder(w).Encode(&respBody); err != nil {
		log.Errorf("Error in encoding response: %+v", err)
	}
}
