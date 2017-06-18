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
	vars := mux.Vars(r)
	vdiskID := vars["vdiskid"]
	aysClient := tools.GetAysConnection(r, api)

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
	serv, resp, err := aysClient.Ays.GetServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("rollback vdisk %s", vdiskID)) {
		return
	}

	// Validate if disk is halted and of type [db, boot]
	var disk Vdisk
	if err := json.Unmarshal(serv.Data, &disk); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Vdisk")
		return
	}
	if string(disk.Status) != "halted" {
		err = fmt.Errorf("Failed to rollback %s, vdisk should be halted", vdiskID)
		tools.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}
	if string(disk.Vdisktype) != "boot" || string(disk.Vdisktype) != "db" {
		err = fmt.Errorf("Failed to rollback %s, rollback is supported for boot or db only", vdiskID)
		tools.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}

	// Create rollback blueprint
	bp := struct {
		Timestamp int `yaml:"timestamp" json:"timestamp"`
	}{
		Timestamp: reqBody.Epoch,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("vdisk__%s", vdiskID)] = bp

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", vdiskID, "rollback", obj)
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
