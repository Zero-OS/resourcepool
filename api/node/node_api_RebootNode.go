package node

import (
	"net/http"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// RebootNode is the handler for POST /nodes/{nodeid}/reboot
// Immediately reboot the machine.
func (api NodeAPI) RebootNode(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeId := vars["nodeid"]

	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			"action":  "reboot",
			"actor":   "node",
			"service": nodeId,
			"force":   true,
		}},
	}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "node", nodeId, "reboot", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		return
	}

	if err = tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err)
		}
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
