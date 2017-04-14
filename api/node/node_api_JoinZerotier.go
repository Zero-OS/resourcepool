package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// JoinZerotier is the handler for POST /nodes/{nodeid}/zerotiers
// Join Zerotier network
func (api NodeAPI) JoinZerotier(w http.ResponseWriter, r *http.Request) {
	var reqBody ZerotierJoin

	nodeID := mux.Vars(r)["nodeid"]

	// decode request
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

	// Create join blueprint
	bp := struct {
		NetworkID string `json:"networkID" yaml:"networkID"`
		Node      string `json:"node" yaml:"node"`
	}{
		NetworkID: reqBody.Nwid,
		Node:      nodeID,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("zerotier__%s_%s", nodeID, reqBody.Nwid)] = bp
	obj["actions"] = []tools.ActionBlock{{
		"action": "install",
		"force":  true,
	}}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "zerotier", reqBody.Nwid, "join", obj)
	if err != nil {
		log.Errorf("error executing blueprint for zerotiers %s join : %+v", reqBody.Nwid, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if err := tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err)
		}
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/zerotiers/%s", nodeID, reqBody.Nwid))
	w.WriteHeader(http.StatusCreated)
}
