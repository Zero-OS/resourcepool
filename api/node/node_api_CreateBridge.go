package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	tools "github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
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

	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

	// Create blueprint
	bp := struct {
		Hwaddr      string                      `json:"hwaddr"`
		Nat         bool                        `json:"nat"`
		NetworkMode EnumBridgeCreateNetworkMode `json:"networkMode"`
		Setting     BridgeCreateSetting         `json:"setting"`
		Node        string                      `json:"node"`
	}{
		Hwaddr:      reqBody.Hwaddr,
		Nat:         reqBody.Nat,
		NetworkMode: reqBody.NetworkMode,
		Setting:     reqBody.Setting,
		Node:        nodeid,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("bridge__%s", reqBody.Name)] = bp
	obj["actions"] = []map[string]string{map[string]string{"action": "install"}}

	if _, err := tools.ExecuteBlueprint(api.AysRepo, reqBody.Name, obj); err != nil {
		log.Errorf("error executing blueprint for bridge %s creation : %+v", reqBody.Name, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/node/%s/bridge/%s", nodeid, reqBody.Name))
	w.WriteHeader(http.StatusCreated)
}
