package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	runs "github.com/zero-os/0-orchestrator/api/run"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateGWForwards is the handler for POST /nodes/{nodeid}/gws/{gwname}/firewall/forwards
// Create a new Portforwarding
func (api NodeAPI) CreateGWForwards(w http.ResponseWriter, r *http.Request) {
	var reqBody PortForward

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
	}

	service, res, err := api.AysAPI.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
		return
	}

	var data CreateGWBP
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s' data", gateway)
		tools.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	if data.Advanced {
		errMessage := fmt.Errorf("Advanced options enabled: cannot add forwards for gateway")
		tools.WriteError(w, http.StatusForbidden, errMessage, "")
		return
	}

	// Check if this portforward exists and return a bad request if the combination exists
	// or update the protocols list if the protocol doesn't exist
	var exists bool
	for i, portforward := range data.Portforwards {
		if portforward.Srcip == reqBody.Srcip && portforward.Srcport == reqBody.Srcport {
			for _, protocol := range portforward.Protocols {
				for _, reqProtocol := range reqBody.Protocols {
					if protocol == reqProtocol {
						err := fmt.Errorf("This protocol, srcip and srcport combination already exists")
						tools.WriteError(w, http.StatusBadRequest, err, "")
						return
					}
				}
			}
			exists = true
			data.Portforwards[i].Protocols = append(data.Portforwards[i].Protocols, reqBody.Protocols...)
		}
	}

	if !exists {
		data.Portforwards = append(data.Portforwards, reqBody)
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gateway)] = data

	api.AysAPI.AuthHeader = r.Header.Get("Authorization")
	run, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errMessage := fmt.Errorf("error executing blueprint for gateway %s update", gateway)
		tools.WriteError(w, httpErr.Resp.StatusCode, errMessage, "")
		return
	}

	response := runs.Run{Runid: run.Key, State: runs.EnumRunState(run.State)}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s/firewall/forwards/%v:%v", nodeID, gateway, reqBody.Srcip, reqBody.Srcport))
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(&response)
}
