package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListGWDHCPHosts is the handler for GET /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts
// List DHCPHosts for specified interface
func (api *NodeAPI) ListGWDHCPHosts(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeId := vars["nodeid"]
	nicInterface := vars["interface"]

	// queryParams := map[string]interface{}{
	// 	"parent": fmt.Sprintf("node.zero-os!%s", nodeId),
	// 	"fields": "nics",
	// }

	// service, res, err := aysClient.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
	// 	return
	// }
	service, err := api.client.GetService("gateway", gateway, fmt.Sprintf("node.zero-os!%s", nodeId), []string{"nics"})
	if err != nil {
		handlers.HandlerError(err)
		return
	}

	var data struct {
		Nics []GWNIC `json:"nics"`
	}
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s' data", gateway)
		httperror.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	var respBody []GWHost
	var exists bool
	for _, nic := range data.Nics {
		if nic.Name == nicInterface {
			if nic.Dhcpserver == nil {
				err = fmt.Errorf("Interface %v has no dhcp", nicInterface)
				httperror.WriteError(w, http.StatusNotFound, err, "")
				return
			}
			exists = true
			respBody = nic.Dhcpserver.Hosts
			break
		}
	}

	if !exists {
		err = fmt.Errorf("Interface %v not found.", nicInterface)
		httperror.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
