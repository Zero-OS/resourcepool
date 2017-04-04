package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	tools "github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

type bridgeBlueprint struct {
	Hwaddr      string                      `json:"hwaddr"`
	Nat         bool                        `json:"nat"`
	NetworkMode EnumBridgeCreateNetworkMode `json:"networkMode"`
	Setting     BridgeCreateSetting         `json:"setting"`
	Node        string                      `json:"node"`
}

// CreateBridge is the handler for POST /node/{nodeid}/bridge
// Creates a new bridge
func (api NodeAPI) CreateBridge(w http.ResponseWriter, r *http.Request) {
	var reqBody BridgeCreate

	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}

	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

	// Create blueprint
	var bp bridgeBlueprint

	bp.Hwaddr = reqBody.Hwaddr
	bp.Nat = reqBody.Nat
	bp.NetworkMode = reqBody.NetworkMode
	bp.Setting = reqBody.Setting
	bp.Node = nodeid

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("bridge__%s", reqBody.Name)] = bp
	obj["actions"] = []map[string]string{map[string]string{"action": "install"}}

	tools.ExecuteBlueprint(w, api.AysRepo, reqBody.Name, obj)
}
