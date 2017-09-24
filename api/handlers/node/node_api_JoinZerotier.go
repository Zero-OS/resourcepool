package node

import (
	"encoding/json"
	"fmt"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// JoinZerotier is the handler for POST /nodes/{nodeid}/zerotiers
// Join Zerotier network
func (api *NodeAPI) JoinZerotier(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody ZerotierJoin

	nodeID := mux.Vars(r)["nodeid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// Create join blueprint
	bp := struct {
		NetworkID string `json:"nwid" yaml:"nwid"`
		Token     string `json:"token,omitempty"`
		Node      string `json:"node" yaml:"node"`
	}{
		NetworkID: reqBody.Nwid,
		Token:     reqBody.Token,
		Node:      nodeID,
	}

	blueprint := ays.Blueprint{
		fmt.Sprintf("zerotier__%s_%s", nodeID, reqBody.Nwid): bp,
		"actions": []ays.ActionBlock{{
			Action:  "install",
			Actor:   "zerotier",
			Service: fmt.Sprintf("%s_%s", nodeID, reqBody.Nwid),
			Force:   true,
		}},
	}
	// obj[fmt.Sprintf("zerotier__%s_%s", nodeID, reqBody.Nwid)] = bp
	// obj["actions"] = []tools.ActionBlock{{
	// 	Action:  "install",
	// 	Actor:   "zerotier",
	// 	Service: fmt.Sprintf("%s_%s", nodeID, reqBody.Nwid),
	// 	Force:   true,
	// }}

	bpName := ays.BlueprintName("zerotier", reqBody.Nwid, "join")
	if _, err := api.client.CreateExecRun(bpName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "zerotier", reqBody.Nwid, "join", obj)
	// errmsg := fmt.Sprintf("error executing blueprint for zerotiers %s join ", reqBody.Nwid)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, err := aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	errmsg := fmt.Sprintf("Error running blueprint for zerotiers %s join ", reqBody.Nwid)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	}
	// 	aysClient.Ays.DeleteServiceByName(fmt.Sprintf("%s_%s", nodeID, reqBody.Nwid), "zerotier", api.AysRepo, nil, nil)
	// 	return
	// }

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/zerotiers/%s", nodeID, reqBody.Nwid))
	w.WriteHeader(http.StatusCreated)
}
