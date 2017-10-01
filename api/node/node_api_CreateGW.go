package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/tools"
)

type CreateGWBP struct {
	Node         string        `json:"node" yaml:"node"`
	Domain       string        `json:"domain" yaml:"domain"`
	Nics         []GWNIC       `json:"nics" yaml:"nics"`
	Httpproxies  []HTTPProxy   `json:"httpproxies" yaml:"httpproxies"`
	Portforwards []PortForward `json:"portforwards" yaml:"portforwards"`
	Advanced     bool          `json:"advanced" yaml:"advanced"`
}

// CreateGW is the handler for POST /nodes/{nodeid}/gws
// Create a new gateway
func (api *NodeAPI) CreateGW(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	var reqBody GWCreate

	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(aysClient, api.AysRepo); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	exists, err := aysClient.ServiceExists("gateway", reqBody.Name, api.AysRepo)
	if err != nil {
		errmsg := fmt.Sprintf("error getting gateway service by name %s ", reqBody.Name)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	if exists {
		tools.WriteError(w, http.StatusConflict, fmt.Errorf("A gateway with name %s already exists", reqBody.Name), "")
		return
	}

	gateway := CreateGWBP{
		Node:         nodeID,
		Domain:       reqBody.Domain,
		Nics:         reqBody.Nics,
		Httpproxies:  reqBody.Httpproxies,
		Portforwards: reqBody.Portforwards,
		Advanced:     false,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", reqBody.Name)] = gateway
	obj["actions"] = []tools.ActionBlock{{Action: "install", Service: reqBody.Name, Actor: "gateway"}}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", reqBody.Name, "install", obj)

	errmsg := fmt.Sprintf("error executing blueprint for gateway %s creation ", reqBody.Name)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}
	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s", nodeID, reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
