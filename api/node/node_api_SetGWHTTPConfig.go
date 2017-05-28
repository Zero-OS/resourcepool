package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// SetGWHTTPConfig is the handler for POST /nodes/{nodeid}/gws/{gwname}/advanced/http
// Set HTTP config
func (api NodeAPI) SetGWHTTPConfig(w http.ResponseWriter, r *http.Request) {
	var gatewayBase GW
	vars := mux.Vars(r)
	gwname := vars["gwname"]
	nodeID := vars["nodeid"]

	node, err := tools.GetConnection(r, api)
	containerID, err := tools.GetContainerId(r, api, node, gwname)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	containerClient := client.Container(node).Client(containerID)
	err = client.Filesystem(containerClient).Upload(r.Body, "/etc/caddy.conf")
	if err != nil {
		fmt.Errorf("Error uploading file to container '%s' at path '%s': %+v.\n", gwname, "/etc/caddy.conf", err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	service, res, err := api.AysAPI.Ays.GetServiceByName(gwname, "gateway", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
		return
	}

	if err := json.Unmarshal(service.Data, &gatewayBase); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
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

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gwname, "update", obj); err != nil {
		fmt.Errorf("error executing blueprint for gateway %s creation : %+v", gwname, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s/advanced/http", nodeID, gwname))
	w.WriteHeader(http.StatusCreated)
}
