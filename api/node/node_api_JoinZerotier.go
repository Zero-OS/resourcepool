package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// JoinZerotier is the handler for POST /nodes/{nodeid}/zerotiers
// Join Zerotier network
func (api NodeAPI) JoinZerotier(w http.ResponseWriter, r *http.Request) {
	var reqBody ZerotierJoin

	nodeID := mux.Vars(r)["nodeid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
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

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("zerotier__%s_%s", nodeID, reqBody.Nwid)] = bp
	obj["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "zerotier",
		Service: fmt.Sprintf("%s_%s", nodeID, reqBody.Nwid),
		Force:   true,
	}}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "zerotier", reqBody.Nwid, "join", obj)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for zerotiers %s join ", reqBody.Nwid)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	if err := tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("Error running blueprint for zerotiers %s join ", reqBody.Nwid)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		}
		api.AysAPI.Ays.DeleteServiceByName(fmt.Sprintf("%s_%s", nodeID, reqBody.Nwid), "zerotier", api.AysRepo, nil, nil)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/zerotiers/%s", nodeID, reqBody.Nwid))
	w.WriteHeader(http.StatusCreated)
}
