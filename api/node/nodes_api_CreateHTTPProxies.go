package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateHTTPProxies is the handler for POST /nodes/{nodeid}/gws/{gwname}/httpproxies
// Create new HTTP proxies
func (api NodeAPI) CreateHTTPProxies(w http.ResponseWriter, r *http.Request) {
	var reqBody HTTPProxy

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]

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
		errMessage := fmt.Errorf("Advanced options enabled: cannot add HTTp proxy for gateway")
		log.Error(errMessage)
		tools.WriteError(w, http.StatusForbidden, errMessage)
		return
	}

	// Check if this proxy exists

	for _, proxy := range data.Httpproxies {
		if proxy.Host == reqBody.Host {
			errMessage := fmt.Errorf("error proxy %+v already exists in gateway %+v", proxy.Host, gateway)
			log.Error(errMessage)
			tools.WriteError(w, http.StatusConflict, errMessage)
			return
		}
	}

	var updatedProxies []HTTPProxy
	data.Httpproxies = append(updatedProxies, reqBody)

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gateway)] = data

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj); err != nil {
		errMessage := fmt.Errorf("error executing blueprint for gateway %s update : %+v", gateway, err)
		tools.WriteError(w, http.StatusInternalServerError, errMessage)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s/httpproxies/%v", nodeID, gateway, reqBody.Host))
	w.WriteHeader(http.StatusCreated)
}
