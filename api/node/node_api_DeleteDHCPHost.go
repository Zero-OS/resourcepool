package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteDHCPHost is the handler for DELETE /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts/{macaddress}
// Delete dhcp host
func (api NodeAPI) DeleteDHCPHost(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeId := vars["nodeid"]
	nicInterface := vars["interface"]
	macaddress := vars["macaddress"]

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
NicsLoop:
	for i, nic := range data.Nics {
		if nic.Name == nicInterface {
			if nic.Dhcpserver == nil {
				err = fmt.Errorf("Interface %v has no dhcp.", nicInterface)
				tools.WriteError(w, http.StatusNotFound, err, "")
				return
			}

			exists = true

			for j, host := range nic.Dhcpserver.Hosts {
				if host.Macaddress == macaddress {
					data.Nics[i].Dhcpserver.Hosts = append(data.Nics[i].Dhcpserver.Hosts[:j],
						data.Nics[i].Dhcpserver.Hosts[j+1:]...)
					break NicsLoop
				}
			}
			err = fmt.Errorf("Dhcp has no host with macaddress %v", macaddress)
			tools.WriteError(w, http.StatusNotFound, err, "")
			return
		}
	}

	if !exists {
		err = fmt.Errorf("Interface %v not found", nicInterface)
		tools.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gateway)] = data

	if _, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj); err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for gateway %s update", gateway)
		if httpErr.Resp.StatusCode/100 == 4 {
			tools.WriteError(w, httpErr.Resp.StatusCode, err, err.Error())
			return
		}
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
