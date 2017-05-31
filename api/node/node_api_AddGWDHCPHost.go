package node

import (
	"encoding/json"
	"net/http"

	"fmt"

	log "github.com/Sirupsen/logrus"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// AddGWDHCPHost is the handler for POST /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts
// Add a dhcp host to a specified interface
func (api NodeAPI) AddGWDHCPHost(w http.ResponseWriter, r *http.Request) {
	var reqBody GWHost

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeId := vars["nodeid"]
	nicInterface := vars["interface"]

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

	var exists bool
	for i, nic := range data.Nics {
		if nic.Name == nicInterface {
			exists = true
			if nic.Dhcpserver == nil {
				err = fmt.Errorf("Interface %v has no dhcp.", nicInterface)
				tools.WriteError(w, http.StatusNotFound, err)
				return
			}
			for _, host := range nic.Dhcpserver.Hosts {
				if host.Macaddress == reqBody.Macaddress {
					err = fmt.Errorf("A host with macaddress %v already exists for this interface.", reqBody.Macaddress)
					tools.WriteError(w, http.StatusBadRequest, err)
					return
				}
				if host.Ipaddress == reqBody.Ipaddress {
					err = fmt.Errorf("A host with ipaddress %v already exists for this interface.", reqBody.Ipaddress)
					tools.WriteError(w, http.StatusBadRequest, err)
					return
				}
			}
			data.Nics[i].Dhcpserver.Hosts = append(data.Nics[i].Dhcpserver.Hosts, reqBody)
			break
		}
	}

	if !exists {
		err = fmt.Errorf("Interface %v not found.", nicInterface)
		tools.WriteError(w, http.StatusNotFound, err)
		return
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gateway)] = data

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj); err != nil {
		fmt.Errorf("error executing blueprint for gateway %s update : %+v", gateway, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
