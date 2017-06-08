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
func (api NodeAPI) CreateBridge(w http.ResponseWriter, r *http.Request) {
	var reqBody BridgeCreate
	vars := mux.Vars(r)
	nodeId := vars["nodeid"]

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
		"parent": fmt.Sprintf("node.zero-os!%s", nodeId),
		"fields": "setting",
	}
	services, resp, err := api.AysAPI.Ays.ListServicesByRole("bridge", api.AysRepo, nil, queryParams)
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
		Node:        nodeId,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("bridge__%s", reqBody.Name)] = bp
	obj["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "bridge",
		Service: reqBody.Name}}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "bridge", reqBody.Name, "install", obj)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for bridge %s creation", reqBody.Name)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if err := tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			errmsg := fmt.Sprintf("error running blueprint for bridge %s creation", reqBody.Name)
			tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		}
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/bridge/%s", nodeId, reqBody.Name))
	w.WriteHeader(http.StatusCreated)
}
