package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	tools "github.com/zero-os/0-orchestrator/api/tools"
	"github.com/zero-os/0-orchestrator/api/validators"
)

// CreateBridge is the handler for POST /node/{nodeid}/bridge
// Creates a new bridge
func (api *NodeAPI) CreateBridge(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	var reqBody BridgeCreate
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	queryParams := map[string]interface{}{
		"parent": fmt.Sprintf("node.zero-os!%s", nodeID),
		"fields": "setting",
	}
	services, resp, err := aysClient.Ays.ListServicesByRole("bridge", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, resp, w, "listing bridges") {
		return
	}

	for _, service := range services {
		bridge := Bridge{
			Name: service.Name,
		}

		if err := json.Unmarshal(service.Data, &bridge); err != nil {
			errmsg := fmt.Sprintf("Error in decoding bridges")
			tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
			return
		}

		if bridge.Name == reqBody.Name {
			tools.WriteError(w, http.StatusConflict, fmt.Errorf("Bridge with name %v already exists", reqBody.Name), "")
			return
		}

		overlaps, err := validators.ValidateCIDROverlap(reqBody.Setting.Cidr, bridge.Setting.Cidr)
		if err != nil {
			tools.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
		if overlaps {
			tools.WriteError(w, http.StatusConflict,
				fmt.Errorf("Cidr %v overlaps with existing cidr %v", reqBody.Setting.Cidr, bridge.Setting.Cidr), "")
			return
		}
	}

	// Create blueprint
	bp := struct {
		Hwaddr      string                      `json:"hwaddr" yaml:"hwaddr"`
		Nat         bool                        `json:"nat" yaml:"nat"`
		NetworkMode EnumBridgeCreateNetworkMode `json:"networkMode" yaml:"networkMode"`
		Setting     BridgeCreateSetting         `json:"setting" yaml:"setting"`
		Node        string                      `json:"node" yaml:"node"`
	}{
		Hwaddr:      reqBody.Hwaddr,
		Nat:         reqBody.Nat,
		NetworkMode: reqBody.NetworkMode,
		Setting:     reqBody.Setting,
		Node:        nodeID,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("bridge__%s", reqBody.Name)] = bp
	obj["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "bridge",
		Service: reqBody.Name}}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "bridge", reqBody.Name, "install", obj)
	errmsg := fmt.Sprintf("error executing blueprint for bridge %s creation", reqBody.Name)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}
	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/bridge/%s", nodeID, reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
