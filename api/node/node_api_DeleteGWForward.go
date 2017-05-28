package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"

	log "github.com/Sirupsen/logrus"
)

// DeleteGWForward is the handler for DELETE /nodes/{nodeid}/gws/{gwname}/firewall/forwards/{forwardid}
// Delete portforward, forwardid = srcip:srcport
func (api NodeAPI) DeleteGWForward(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeId := vars["nodeid"]
	forwardId := vars["forwardid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.g8os!%s", nodeId),
	}

	service, res, err := api.AysAPI.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting storagepool service") {
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
		errMessage := fmt.Errorf("Advanced options enabled: cannot delete forwards for gateway")
		tools.WriteError(w, http.StatusForbidden, errMessage)
		return
	}

	var updatedForwards []PortForward
	// Check if this forwardid exists
	var exists bool
	for _, portforward := range data.Portforwards {
		portforwadId := fmt.Sprintf("%v:%v", portforward.Srcip, portforward.Srcport)
		if portforwadId == forwardId {
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

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gateway)] = data

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj); err != nil {
		fmt.Errorf("error executing blueprint for gateway %s update : %+v", gateway, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
