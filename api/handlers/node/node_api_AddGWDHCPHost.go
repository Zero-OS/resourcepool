package node

import (
	"encoding/json"
	"net/http"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// AddGWDHCPHost is the handler for POST /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts
// Add a dhcp host to a specified interface
func (api *NodeAPI) AddGWDHCPHost(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody GWHost

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	vars := mux.Vars(r)
	gateway := vars["gwname"]
	nodeID := vars["nodeid"]
	nicInterface := vars["interface"]

	parent := fmt.Sprintf("node.zero-os!%s", nodeID)

	service, err := api.client.GetService("gateway", gateway, parent, nil)
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}

	var data CreateGWBP
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s' data", gateway)
		httperror.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	var exists bool
	for i, nic := range data.Nics {
		if nic.Name == nicInterface {
			exists = true
			if nic.Dhcpserver == nil {
				err = fmt.Errorf("Interface %v has no dhcp.", nicInterface)
				httperror.WriteError(w, http.StatusNotFound, err, "")
				return
			}
			for _, host := range nic.Dhcpserver.Hosts {
				if host.Macaddress == reqBody.Macaddress {
					err = fmt.Errorf("A host with macaddress %v already exists for this interface.", reqBody.Macaddress)
					httperror.WriteError(w, http.StatusBadRequest, err, "")
					return
				}
				if host.Ipaddress == reqBody.Ipaddress {
					err = fmt.Errorf("A host with ipaddress %v already exists for this interface.", reqBody.Ipaddress)
					httperror.WriteError(w, http.StatusBadRequest, err, "")
					return
				}
			}
			data.Nics[i].Dhcpserver.Hosts = append(data.Nics[i].Dhcpserver.Hosts, reqBody)
			break
		}
	}

	if !exists {
		err = fmt.Errorf("Interface %v not found.", nicInterface)
		httperror.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	serviceName := fmt.Sprintf("gateway__%s", gateway)
	blueprint := ays.Blueprint{serviceName: data}

	blueprintName := ays.BlueprintName("gateway", gateway, "update")

	if err := api.client.CreateExec(blueprintName, blueprint); err != nil {
		handlers.HandleError(w, err)
		return
	}

	// if err := api.client.CreateBlueprint(bpName, blueprint); err != nil {
	// 	err.Handle(w, http.StatusInternalServerError)
	// 	return
	// }
	// _, err = aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gateway, "update", obj)

	// errmsg := fmt.Sprintf("error executing blueprint for gateway %s update", gateway)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	w.WriteHeader(http.StatusNoContent)
}
