package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/mux"
	tools "github.com/zero-os/0-orchestrator/api/tools"
)

// CreateBridge is the handler for POST /node/{nodeid}/bridge
// Creates a new bridge
func (api NodeAPI) CreateBridge(w http.ResponseWriter, r *http.Request) {
	var reqBody BridgeCreate

	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// check that service exists
	_, _, err := api.AysAPI.Ays.GetServiceByName(reqBody.Name, "bridge", api.AysRepo, nil, nil)
	if err == nil {
		err = fmt.Errorf("Bridge already exists")
		tools.WriteError(w, http.StatusConflict, err)
		return
	}

	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

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
		Node:        nodeid,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("bridge__%s", reqBody.Name)] = bp
	obj["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "bridge",
		Service: reqBody.Name}}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "bridge", reqBody.Name, "install", obj)
	if err != nil {
		log.Errorf("error executing blueprint for bridge %s creation : %+v", reqBody.Name, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if err := tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err)
		}
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/bridge/%s", nodeid, reqBody.Name))
	w.WriteHeader(http.StatusCreated)
}
