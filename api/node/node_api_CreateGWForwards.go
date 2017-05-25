package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// nodeidgwsgwnamefirewallforwardsPost is the handler for POST /nodes/{nodeid}/gws/{gwname}/firewall/forwards
// Create a new Portforwarding
func (api NodeAPI) CreateGWForwards(w http.ResponseWriter, r *http.Request) {
	var reqBody PortForward

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeId := vars["nodeid"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.g8os!%s", nodeId),
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

	// Check if this portforward exists and return a bad request if the combination exists
	// or update the protocols list if the protocol doesn't exist
	var exists bool
	for i, portforward := range data.Portforwards {
		if portforward.Srcip == reqBody.Srcip && portforward.Srcport == reqBody.Srcport {
			for _, protocol := range portforward.Protocols {
				for _, reqProtocol := range reqBody.Protocols {
					if protocol == reqProtocol {
						err := fmt.Errorf("This protocol, srcip and srcport combination already exists.")
						log.Error(err)
						tools.WriteError(w, http.StatusBadRequest, err)
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

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj); err != nil {
		errMessage := fmt.Errorf("error executing blueprint for gateway %s update : %+v", gateway, err)
		tools.WriteError(w, http.StatusInternalServerError, errMessage)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s/firewall/forwards/%v:%v", nodeId, gateway, reqBody.Srcip, reqBody.Srcport))
	w.WriteHeader(http.StatusCreated)
}
