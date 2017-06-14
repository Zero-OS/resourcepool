package vdisk

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	runs "github.com/zero-os/0-orchestrator/api/run"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// RollbackVdisk is the handler for POST /vdisks/{vdiskid}/rollback
// Rollback a vdisk to a previous state
func (api VdisksAPI) RollbackVdisk(w http.ResponseWriter, r *http.Request) {
	var reqBody VdiskRollback

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

	// Create rollback blueprint
	vdiskID := mux.Vars(r)["vdiskid"]
	bp := struct {
		Timestamp uint64 `yaml:"timestamp" json:"timestamp"`
	}{
		Timestamp: reqBody.Epoch,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("vdisk__%s", vdiskID)] = bp
	obj["actions"] = []tools.ActionBlock{{Service: vdiskID, Actor: "vdisk", Action: "rollback"}}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "vdisk", vdiskID, "rollback", obj)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for vm %s creation", vdiskID)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	response := runs.Run{Runid: run.Key, State: runs.EnumRunState(run.State)}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(&response)
}
