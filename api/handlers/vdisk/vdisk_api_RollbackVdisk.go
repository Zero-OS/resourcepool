package vdisk

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/httperror"
)

// RollbackVdisk is the handler for POST /vdisks/{vdiskid}/rollback
// Rollback a vdisk to a previous state
func (api *VdisksAPI) RollbackVdisk(w http.ResponseWriter, r *http.Request) {

	var reqBody VdiskRollback
	vars := mux.Vars(r)
	vdiskID := vars["vdiskid"]
	// aysClient := tools.GetAysConnection(r, api)

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

	serv, err := api.client.GetService("vdisk", vdiskID, "", nil)
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// serv, resp, err := aysClient.Ays.GetServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)

	// if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("rollback vdisk %s", vdiskID)) {
	// 	return
	// }

	// Validate if disk is halted and of type [db, boot]
	var disk Vdisk
	if err := json.Unmarshal(serv.Data, &disk); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Vdisk")
		return
	}
	// Make sure the disk is attached to a tlogStoragecluster
	if disk.ObjectStoragecluster == "" {
		err := fmt.Errorf("Failed to rollback %s, vdisk needs to be attached to a Object Cluster", vdiskID)
		httperror.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}
	// Make sure  this disk is attached to a vm
	var vmFound = false
	for _, service := range serv.Consumers {
		if service.Role == "vm" {
			vmFound = true
			break
		}
	}
	if !vmFound {
		err := fmt.Errorf("Failed to rollback %s, vdisk needs to be attached to a machine", vdiskID)
		httperror.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}
	if string(disk.Status) != "halted" {
		err := fmt.Errorf("Failed to rollback %s, vdisk should be halted", vdiskID)
		httperror.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}
	if disk.Vdisktype != EnumVdiskVdisktypeboot && disk.Vdisktype != EnumVdiskVdisktypedb {
		err := fmt.Errorf("Failed to rollback %s, rollback is supported for boot or db only", vdiskID)
		httperror.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}

	// Create rollback blueprint
	bp := struct {
		Timestamp int `yaml:"timestamp" json:"timestamp"`
	}{
		Timestamp: reqBody.Epoch,
	}

	obj := ays.Blueprint{
		fmt.Sprintf("vdisk__%s", vdiskID): bp,
	}
	// obj[] = bp

	bpName := ays.BlueprintName("vdisk", vdiskID, "rollback")
	if _, err := api.client.CreateExecRun(bpName, obj, true); err != nil {
		if ayserr, ok := err.(*ays.Error); ok {
			ayserr.Handle(w, http.StatusInternalServerError)
		} else {
			httperror.WriteError(w, http.StatusInternalServerError, err, "fail to create vdisk")
		}
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", vdiskID, "rollback", obj)
	// errmsg := fmt.Sprintf("error executing blueprint for vm %s creation", vdiskID)
	// if tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }

	w.WriteHeader(http.StatusCreated)

}
