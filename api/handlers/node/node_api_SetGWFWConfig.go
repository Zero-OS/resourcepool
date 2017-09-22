package node

import (
	"encoding/json"
	"fmt"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"net/http"

	"github.com/gorilla/mux"
	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// SetGWFWConfig is the handler for POST /nodes/{nodeid}/gws/{gwname}/advanced/firewall
// Set FW config
func (api *NodeAPI) SetGWFWConfig(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var gatewayBase GW
	vars := mux.Vars(r)
	gwname := vars["gwname"]
	nodeID := vars["nodeid"]

	node, err := api.client.GetNodeConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}
	containerID, err := api.client.GetContainerID(r, gwname)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to get container id")
		return
	}

	containerClient := client.Container(node).Client(containerID)
	err = client.Filesystem(containerClient).Upload(r.Body, "/etc/nftables.conf")
	if err != nil {
		errmsg := fmt.Sprintf("Error uploading file to container '%s' at path '%s'.\n", gwname, "/etc/nftables.conf")
		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	service, err := api.client.GetService("gateway", gwname)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	// service, res, err := aysClient.Ays.GetServiceByName(gwname, "gateway", api.AysRepo, nil, nil)

	// if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
	// 	return
	// }

	if err := json.Unmarshal(service.Data, &gatewayBase); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
		return
	}

	gatewayNew := CreateGWBP{
		Node:         nodeID,
		Domain:       gatewayBase.Domain,
		Nics:         gatewayBase.Nics,
		Httpproxies:  gatewayBase.Httpproxies,
		Portforwards: gatewayBase.Portforwards,
		Advanced:     true,
	}

	bp := ays.Blueprint{
		fmt.Sprintf("gateway__%s", gwname): gatewayNew,
	}
	bpName := ays.BlueprintName("gateway", gwname, "update")

	if err := api.client.CreateExec(bpName, bp); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// obj[] = gatewayNew

	// _, err = aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gwname, "update", obj)

	// errmsg := fmt.Sprintf("error executing blueprint for gateway %s creation : %+v", gwname, err)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s/advanced/http", nodeID, gwname))
	w.WriteHeader(http.StatusCreated)
}
