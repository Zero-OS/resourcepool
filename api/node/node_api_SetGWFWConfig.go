package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// SetGWFWConfig is the handler for POST /nodes/{nodeid}/gws/{gwname}/advanced/firewall
// Set FW config
func (api NodeAPI) SetGWFWConfig(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var gatewayBase GW
	vars := mux.Vars(r)
	gwname := vars["gwname"]
	nodeID := vars["nodeid"]

	node, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}
	containerID, err := tools.GetContainerId(r, api, node, gwname)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to get container id")
		return
	}

	containerClient := client.Container(node).Client(containerID)
	err = client.Filesystem(containerClient).Upload(r.Body, "/etc/nftables.conf")
	if err != nil {
		errmsg := fmt.Sprintf("Error uploading file to container '%s' at path '%s'.\n", gwname, "/etc/nftables.conf")
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	service, res, err := aysClient.Ays.GetServiceByName(gwname, "gateway", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
		return
	}

	if err := json.Unmarshal(service.Data, &gatewayBase); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
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

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gwname)] = gatewayNew

	if _, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gwname, "update", obj); err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for gateway %s creation : %+v", gwname, err)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s/advanced/http", nodeID, gwname))
	w.WriteHeader(http.StatusCreated)
}
