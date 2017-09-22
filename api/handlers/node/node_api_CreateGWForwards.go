package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/httperror"
)

// CreateGWForwards is the handler for POST /nodes/{nodeid}/gws/{gwname}/firewall/forwards
// Create a new Portforwarding
func (api *NodeAPI) CreateGWForwards(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody PortForward

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	vars := mux.Vars(r)
	gatewayName := vars["gwname"]
	nodeID := vars["nodeid"]

	// queryParams := map[string]interface{}{
	// 	"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
	// }
	// service, res, err := aysClient.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
	// 	return
	// }

	parent := fmt.Sprintf("node.zero-os!%s", nodeID)
	service, err := api.client.GetService("gateway", gatewayName, parent, nil)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	var gateway CreateGWBP
	if err := json.Unmarshal(service.Data, &gateway); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s' data", gatewayName)
		httperror.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	if gateway.Advanced {
		errMessage := fmt.Errorf("Advanced options enabled: cannot add forwards for gateway")
		httperror.WriteError(w, http.StatusForbidden, errMessage, "")
		return
	}

	// Check if this portforward exists and return a bad request if the combination exists
	// or update the protocols list if the protocol doesn't exist
	var exists bool
	for i, portforward := range gateway.Portforwards {
		if portforward.Srcip == reqBody.Srcip && portforward.Srcport == reqBody.Srcport {
			for _, protocol := range portforward.Protocols {
				for _, reqProtocol := range reqBody.Protocols {
					if protocol == reqProtocol {
						err := fmt.Errorf("This protocol, srcip and srcport combination already exists")
						httperror.WriteError(w, http.StatusBadRequest, err, "")
						return
					}
				}
			}
			exists = true
			gateway.Portforwards[i].Protocols = append(gateway.Portforwards[i].Protocols, reqBody.Protocols...)
		}
	}

	if !exists {
		gateway.Portforwards = append(gateway.Portforwards, reqBody)
	}

	// obj[] = data

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj)
	// errmsg := fmt.Sprintf("error executing blueprint for gateway %s update", gateway)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }

	serviceName := fmt.Sprintf("gateway__%s", gatewayName)
	blueprint := ays.Blueprint{
		serviceName: gateway,
	}
	blueprintName := ays.BlueprintName("gateway", gatewayName, "update")
	if _, err := api.client.CreateExecRun(blueprintName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s/firewall/forwards/%v:%v", nodeID, gatewayName, reqBody.Srcip, reqBody.Srcport))
	w.WriteHeader(http.StatusCreated)

}
