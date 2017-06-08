package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetHTTPProxies is the handler for GET /nodes/{nodeid}/gws/{gwname}/httpproxies/{proxyid}
// Get list for HTTP proxies
func (api NodeAPI) GetHTTPProxy(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]
	proxyID := vars["proxyid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
		"fields": "httpproxies",
	}

	service, res, err := api.AysAPI.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
		return
	}

	var proxies struct {
		HTTPProxies []HTTPProxy `json:"httpproxies"`
	}

	if err := json.Unmarshal(service.Data, &proxies); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s'", gateway)
		tools.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	var respBody HTTPProxy

	exists := false
	for _, proxy := range proxies.HTTPProxies {
		if proxy.Host == proxyID {
			respBody = proxy
			exists = true
			break
		}
	}

	if !exists {
		errMessage := fmt.Errorf("error proxy %+v is not found in gateway %+v", proxyID, gateway)
		tools.WriteError(w, http.StatusNotFound, errMessage, "")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
