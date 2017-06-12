package run

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetRunState is the handler for GET /runs
// Get Run Status
func (api RunsAPI) GetRunState(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	runid := vars["runid"]
	run, resp, err := api.AysAPI.Ays.GetRun(runid, api.AysRepo, nil, nil)
	if err != nil {
		tools.WriteError(w, resp.StatusCode, err, "Error getting run")
	}

	respBody := Run{Runid: run.Key, State: run.State}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
