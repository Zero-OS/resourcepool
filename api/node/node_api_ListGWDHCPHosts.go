package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// ListGWDHCPHosts is the handler for GET /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts
// List DHCPHosts for specified interface
func (api NodeAPI) ListGWDHCPHosts(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeId := vars["nodeid"]
	nicInterface := vars["interface"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.g8os!%s", nodeId),
		"fields": "nics",
	}

	service, res, err := api.AysAPI.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
		return
	}

	var data struct {
		Nics []GWNIC `json:"nics"`
	}
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Errorf("Error Unmarshal gateway service '%s' data: %+v", gateway, err)
		log.Error(errMessage)
		tools.WriteError(w, http.StatusInternalServerError, errMessage)
		return
	}

	var respBody []GWHost
	var exists bool
	for _, nic := range data.Nics {
		if nic.Name == nicInterface {
			if nic.Dhcpserver == nil {
				err = fmt.Errorf("Interface %v has no dhcp", nicInterface)
				tools.WriteError(w, http.StatusNotFound, err)
				return
			}
			exists = true
			respBody = nic.Dhcpserver.Hosts
			break
		}
	}

	if !exists {
		err = fmt.Errorf("Interface %v not found.", nicInterface)
		tools.WriteError(w, http.StatusNotFound, err)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
