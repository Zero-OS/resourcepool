package vdisk

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/vdiskstorage"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// RollbackVdisk is the handler for POST /vdisks/{vdiskid}/rollback
// Rollback a vdisk to a previous state
func (api *VdisksAPI) RollbackVdisk(w http.ResponseWriter, r *http.Request) {

	var reqBody VdiskRollback
	vars := mux.Vars(r)
	vdiskID := vars["vdiskid"]
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
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

	// Make sure the disk is attached to a tlogStoragecluster
	serv, resp, err = aysClient.Ays.GetServiceByName(disk.Vdiskstorage, "vdiskstorage", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("rollback vdisk %s", vdiskID)) {
		return
	}

	var vdiskstorage vdiskstorage.VdiskStorage
	if err := json.Unmarshal(serv.Data, &vdiskstorage); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Vdisk")
		return
	}

	if vdiskstorage.ObjectCluster == "" {
		err = fmt.Errorf("Failed to rollback %s, vdisk needs to be attached to a Object Cluster", vdiskID)
		tools.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}
	// Make sure  this disk is attached to a vm
	if string(disk.Status) != "halted" {
		err = fmt.Errorf("Failed to rollback %s, vdisk should be halted", vdiskID)
		tools.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}
	if disk.Vdisktype != EnumVdiskVdisktypeboot && disk.Vdisktype != EnumVdiskVdisktypedb {
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
	errmsg := fmt.Sprintf("error executing blueprint for vm %s creation", vdiskID)
	if tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}

	w.WriteHeader(http.StatusCreated)
}
