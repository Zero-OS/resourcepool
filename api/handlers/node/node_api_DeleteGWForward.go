package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// DeleteGWForward is the handler for DELETE /nodes/{nodeid}/gws/{gwname}/firewall/forwards/{forwardid}
// Delete portforward, forwardid = srcip:srcport
func (api *NodeAPI) DeleteGWForward(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]
	forwardID := vars["forwardid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
	}

	// service, res, err := aysClient.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
	// 	return
	// }
	nodeService, err := api.client.GetService("gateway", gateway, "", []string{"RedisAddr"})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	var data CreateGWBP
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s' data", gateway)
		httperror.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	if data.Advanced {
		errMessage := fmt.Errorf("Advanced options enabled: cannot delete forwards for gateway")
		httperror.WriteError(w, http.StatusForbidden, errMessage, "")
		return
	}

	var updatedForwards []PortForward
	// Check if this forwardid exists
	var exists bool
	for _, portforward := range data.Portforwards {
		portforwadID := fmt.Sprintf("%v:%v", portforward.Srcip, portforward.Srcport)
		if portforwadID == forwardID {
			exists = true
		} else {
			updatedForwards = append(updatedForwards, portforward)
		}
	}

	if !exists {
		w.WriteHeader(http.StatusNotFound)
		return
	}

	data.Portforwards = updatedForwards

	obj := ays.Blueprint{
		fmt.Sprintf("gateway__%s", gateway): data,
	}
	// obj[fmt.Sprintf("gateway__%s", gateway)] = data
	bpName := ays.BlueprintName("gateway", gateway, "update")
	_, err := api.client.CreateExec(bpName, obj)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	// _, err = aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj)

	// errmsg := fmt.Sprintf("error executing blueprint for gateway %s update ", gateway)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	w.WriteHeader(http.StatusNoContent)
}
