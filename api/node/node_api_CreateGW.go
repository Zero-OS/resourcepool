package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"

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
func (api NodeAPI) CreateGW(w http.ResponseWriter, r *http.Request) {
	var reqBody GWCreate

	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
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

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", reqBody.Name, "install", obj); err != nil {
		log.Errorf("error executing blueprint for gateway %s creation : %+v", reqBody.Name, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s", nodeID, reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
