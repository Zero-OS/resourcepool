package vdisk

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteVdisk is the handler for DELETE /vdisks/{vdiskid}
// Delete Vdisk
func (api *VdisksAPI) DeleteVdisk(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	vdiskID := vars["vdiskid"]

	_, resp, err := aysClient.Ays.GetServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)

	if err != nil {
		errmsg := fmt.Sprintf("error executing blueprint for vdisk %s deletion", vdiskID)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	if resp.StatusCode == http.StatusNotFound {
		w.WriteHeader(http.StatusNoContent)
		return
	}

	// Prevent deletion of nonempty clusters
	query := map[string]interface{}{
		"consume": fmt.Sprintf("vdisk!%s", vdiskID),
	}
	services, res, err := aysClient.Ays.ListServicesByRole("vm", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, res, w, "listing vms") {
		return
	}

	if len(services) > 0 {
		err := fmt.Errorf("Can't delete vdisk that is attached to VM")
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "delete",
			Actor:   "vdisk",
			Service: vdiskID,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", vdiskID, "delete", blueprint)
	msg := fmt.Sprintf("Error executing blueprint for vdisk deletion")
	if !tools.HandleExecuteBlueprintResponse(err, w, msg) {
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for vdisk deletion")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for vdisk deletion")
		}
		return
	}

	_, err = aysClient.Ays.DeleteServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)

	if err != nil {
		errmsg := fmt.Sprintf("Error in deleting vdisk %s ", vdiskID)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
