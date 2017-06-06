package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteHTTPProxies is the handler for DELETE /nodes/{nodeid}/gws/{gwname}/httpproxies
// Delete HTTP proxy
func (api NodeAPI) DeleteHTTPProxies(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]
	proxyID := vars["proxyid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.g8os!%s", nodeID),
	}

	service, res, err := api.AysAPI.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
		return
	}

	var data CreateGWBP
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Errorf("Error Unmarshal gateway service '%s' data: %+v", gateway, err)
		log.Error(errMessage)
		tools.WriteError(w, http.StatusInternalServerError, errMessage)
		return
	}

	if data.Advanced {
		errMessage := fmt.Errorf("Advanced options enabled: cannot delete http proxy for gateway")
		log.Errorf("%v: %v", errMessage, gateway)
		tools.WriteError(w, http.StatusForbidden, errMessage)
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
		log.Error(errMessage)
		tools.WriteError(w, http.StatusNotFound, errMessage)
		return
	}

	data.Httpproxies = updatedProxies

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gateway)] = data

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj); err != nil {
		log.Errorf("error executing blueprint for gateway %s update : %+v", gateway, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
