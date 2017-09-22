package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateHTTPProxies is the handler for POST /nodes/{nodeid}/gws/{gwname}/httpproxies
// Create new HTTP proxies
func (api *NodeAPI) CreateHTTPProxies(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody HTTPProxy

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]

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
		httperror.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	if data.Advanced {
		errMessage := fmt.Errorf("Advanced options enabled: cannot add HTTp proxy for gateway")
		httperror.WriteError(w, http.StatusForbidden, errMessage, "")
		return
	}

	// Check if this proxy exists
	for _, proxy := range data.Httpproxies {
		if proxy.Host == reqBody.Host {
			errMessage := fmt.Errorf("error proxy %+v already exists in gateway %+v", proxy.Host, gateway)
			httperror.WriteError(w, http.StatusConflict, errMessage, "")
			return
		}
	}

	data.Httpproxies = append(data.Httpproxies, reqBody)

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gateway)] = data

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj)
	errMessage := fmt.Sprintf("error executing blueprint for gateway %s", gateway)
	if !tools.HandleExecuteBlueprintResponse(err, w, errMessage) {
		return
	}

	if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
		return
	}
	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s/httpproxies/%v", nodeID, gateway, reqBody.Host))
	w.WriteHeader(http.StatusCreated)

}
