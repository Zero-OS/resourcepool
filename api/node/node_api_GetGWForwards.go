package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// GetGWForwards is the handler for GET /nodes/{nodeid}/gws/{gwname}/firewall/forwards
// Get list for IPv4 Forwards
func (api NodeAPI) GetGWForwards(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeId := vars["nodeid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeId),
		"fields": "portforwards",
	}

	service, res, err := api.AysAPI.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
		return
	}

	var respBody struct {
		PortForwards []PortForward `json:"portforwards"`
	}

	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		errMessage := fmt.Errorf("Error Unmarshal gateway service '%s' data: %+v", gateway, err)
		log.Error(errMessage)
		tools.WriteError(w, http.StatusInternalServerError, errMessage)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(respBody.PortForwards)
}
