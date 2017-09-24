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

// DeleteDHCPHost is the handler for DELETE /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts/{macaddress}
// Delete dhcp host
func (api *NodeAPI) DeleteDHCPHost(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]
	nicInterface := vars["interface"]
	macaddress := vars["macaddress"]

	// queryParams := map[string]interface{}{
	// 	"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
	// }

	parent := fmt.Sprintf("node.zero-os!%s", nodeID)
	service, err := api.client.GetService("gateway", gateway, parent, nil)
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

	var exists bool
NicsLoop:
	for i, nic := range data.Nics {
		if nic.Name == nicInterface {
			if nic.Dhcpserver == nil {
				err = fmt.Errorf("Interface %v has no dhcp.", nicInterface)
				httperror.WriteError(w, http.StatusNotFound, err, "")
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
			httperror.WriteError(w, http.StatusNotFound, err, "")
			return
		}
	}

	if !exists {
		err = fmt.Errorf("Interface %v not found", nicInterface)
		httperror.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	serviceName := fmt.Sprintf("gateway__%s", gateway)
	blueprint := ays.Blueprint{
		serviceName: data,
	}
	blueprintName := ays.BlueprintName("gateway", gateway, "update")
	if err := api.client.CreateExec(blueprintName, blueprint); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// _, err = aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj)

	// errmsg := fmt.Sprintf("error executing blueprint for gateway %s update", gateway)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	w.WriteHeader(http.StatusNoContent)
}
