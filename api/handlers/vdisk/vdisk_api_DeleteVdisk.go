package vdisk

import (
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// DeleteVdisk is the handler for DELETE /vdisks/{vdiskid}
// Delete Vdisk
func (api *VdisksAPI) DeleteVdisk(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	vdiskID := vars["vdiskid"]

	exists, err := api.client.IsServiceExists("vdisk", vdiskID)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	if !exists {
		httperror.WriteError(w, http.StatusNotFound, fmt.Errorf("A vdisk with ID %s does not exist", vdiskID), "")
		return
	}
	// _, resp, err := aysClient.Ays.GetServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)

	// if err != nil {
	// 	errmsg := fmt.Sprintf("error executing blueprint for vdisk %s deletion", vdiskID)
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	return
	// }

	// if resp.StatusCode == http.StatusNotFound {
	// 	httperror.WriteError(w, http.StatusNotFound, fmt.Errorf("A vdisk with ID %s does not exist", vdiskID), "")
	// 	return
	// }

	// execute the delete action of the snapshot
	blueprint := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "delete",
			Actor:   "vdisk",
			Service: vdiskID,
			Force:   true,
		}},
	}

	bpName := ays.BlueprintName("vdisk", vdiskID, "delete")
	if _, err := api.client.CreateExecRun(bpName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", vdiskID, "delete", blueprint)
	// msg := fmt.Sprintf("Error executing blueprint for vdisk deletion")
	// if !tools.HandleExecuteBlueprintResponse(err, w, msg) {
	// 	return
	// }

	// // Wait for the delete job to be finshed before we delete the service
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for vdisk deletion")
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for vdisk deletion")
	// 	}
	// 	return
	// }

	// _, err = aysClient.Ays.DeleteServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)
	if err := api.client.DeleteService("vdisk", vdiskID); err != nil {
		handlers.HandleError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
