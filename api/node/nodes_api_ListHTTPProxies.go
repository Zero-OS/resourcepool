package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListHTTPProxies is the handler for GET /nodes/{nodeid}/gws/{gwname}/httpproxies
// Get list for HTTP proxies
func (api NodeAPI) ListHTTPProxies(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
		"fields": "httpproxies",
	}

	service, res, err := api.AysAPI.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
		return
	}

	var respBody struct {
		HTTPProxies []HTTPProxy `json:"httpproxies"`
	}

	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s'", gateway)
		tools.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(respBody.HTTPProxies)
}
