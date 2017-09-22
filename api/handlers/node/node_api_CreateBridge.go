package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/httperror"
	tools "github.com/zero-os/0-orchestrator/api/tools"
	"github.com/zero-os/0-orchestrator/api/validators"
)

// CreateBridge is the handler for POST /node/{nodeid}/bridge
// Creates a new bridge
func (api *NodeAPI) CreateBridge(w http.ResponseWriter, r *http.Request) {
	var reqBody BridgeCreate
	vars := mux.Vars(r)
	nodeId := vars["nodeid"]

	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// queryParams := map[string]interface{}{
	// 	"parent": fmt.Sprintf("node.zero-os!%s", nodeId),
	// 	"fields": "setting",
	// }
	// services, resp, err := aysClient.Ays.ListServicesByRole("bridge", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, resp, w, "listing bridges") {
	// 	return
	// }

	listOptions := ListServiceOpt{Parent: fmt.Sprintf("node.zero-os!%s", nodeId), Fields: []string{"setting"}}
	services, err := api.client.ListServices("bridge", listOptions)
	if err != nil {
		api.client.HandleError(w, err)
		return
	}

	for _, service := range services {
		bridge := Bridge{
			Name: service.Name,
		}

		if err := json.Unmarshal(service.Data, &bridge); err != nil {
			errmsg := fmt.Sprintf("Error in decoding bridges")
			httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
			return
		}

		if bridge.Name == reqBody.Name {
			httperror.WriteError(w, http.StatusConflict, fmt.Errorf("Bridge with name %v already exists", reqBody.Name), "")
			return
		}

		overlaps, err := validators.ValidateCIDROverlap(reqBody.Setting.Cidr, bridge.Setting.Cidr)
		if err != nil {
			httperror.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
		if overlaps {
			httperror.WriteError(w, http.StatusConflict,
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
		Node:        nodeId,
	}

	// obj := make(map[string]interface{})
	// obj[fmt.Sprintf("bridge__%s", reqBody.Name)] = bp
	// obj["actions"] = []tools.ActionBlock{{
	// 	Action:  "install",
	// 	Actor:   "bridge",
	// 	Service: reqBody.Name}}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "bridge", reqBody.Name, "install", obj)
	// errmsg := fmt.Sprintf("error executing blueprint for bridge %s creation", reqBody.Name)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }

	serviceName := fmt.Sprintf("bridge__%s", reqBody.Name)
	blueprint := Blueprint{
		serviceName: bp,
		"actions":   []tools.ActionBlock{{Action: "install", Actor: "bridge", Service: reqBody.Name}},
	}
	blueprintName := ays.BlueprintName("bridge", reqBody.Name, "create")
	if _, err := api.client.CreateExecRun(blueprintName, blueprint, true); err != nil {
		api.client.HandleError(w, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/bridge/%s", nodeId, reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
