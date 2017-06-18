package run

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetRunState is the handler for GET /runs/{runid}/wait
// Get Run Status
func (api RunsAPI) WaitOnRun(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	runid := vars["runid"]
	run, resp, err := aysClient.Ays.GetRun(runid, api.AysRepo, nil, nil)
	if err != nil {
		tools.WriteError(w, resp.StatusCode, err, "Error getting run")
	}

	if err := aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error waiting on run %s", run.Key)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		}
		return
	}

	respBody := Run{Runid: run.Key, State: EnumRunState(run.State)}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
