package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteHTTPProxies is the handler for DELETE /nodes/{nodeid}/gws/{gwname}/httpproxies
// Delete HTTP proxy
func (api *NodeAPI) DeleteHTTPProxies(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]
	proxyID := vars["proxyid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
	}

	service, res, err := aysClient.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
		return
	}

	var data CreateGWBP
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s'", gateway)
		tools.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	if data.Advanced {
		errMessage := "Advanced options enabled: cannot delete http proxy for gateway"
		tools.WriteError(w, http.StatusForbidden, fmt.Errorf("%v: %v", errMessage, gateway), errMessage)
		return
	}

	var updatedProxies []HTTPProxy
	// Check if this proxy exists
	var exists bool
	for _, proxy := range data.Httpproxies {
		if proxy.Host == proxyID {
			exists = true
		} else {
			updatedProxies = append(updatedProxies, proxy)
		}
	}

	if !exists {
		errMessage := fmt.Errorf("error proxy %+v is not found in gateway %+v", proxyID, gateway)
		tools.WriteError(w, http.StatusNotFound, errMessage, "")
		return
	}

	data.Httpproxies = updatedProxies

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gateway)] = data

	_, err = aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj)

	errmsg := fmt.Sprintf("error executing blueprint for gateway %s update ", gateway)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
