package node

import (
	"encoding/json"
	"net/http"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// AddGWDHCPHost is the handler for POST /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts
// Add a dhcp host to a specified interface
func (api NodeAPI) AddGWDHCPHost(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody GWHost

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeId := vars["nodeid"]
	nicInterface := vars["interface"]

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeId),
	}

	service, res, err := aysClient.Ays.GetServiceByName(gateway, "gateway", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting gateway service") {
		return
	}

	var data CreateGWBP
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s' data", gateway)
		tools.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	var exists bool
	for i, nic := range data.Nics {
		if nic.Name == nicInterface {
			exists = true
			if nic.Dhcpserver == nil {
				err = fmt.Errorf("Interface %v has no dhcp.", nicInterface)
				tools.WriteError(w, http.StatusNotFound, err, "")
				return
			}
			for _, host := range nic.Dhcpserver.Hosts {
				if host.Macaddress == reqBody.Macaddress {
					err = fmt.Errorf("A host with macaddress %v already exists for this interface.", reqBody.Macaddress)
					tools.WriteError(w, http.StatusBadRequest, err, "")
					return
				}
				if host.Ipaddress == reqBody.Ipaddress {
					err = fmt.Errorf("A host with ipaddress %v already exists for this interface.", reqBody.Ipaddress)
					tools.WriteError(w, http.StatusBadRequest, err, "")
					return
				}
			}
			data.Nics[i].Dhcpserver.Hosts = append(data.Nics[i].Dhcpserver.Hosts, reqBody)
			break
		}
	}

	if !exists {
		err = fmt.Errorf("Interface %v not found.", nicInterface)
		tools.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gateway)] = data

	if _, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj); err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for gateway %s update", gateway)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
