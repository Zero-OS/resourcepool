package vdisk

import (
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// DeleteVdisk is the handler for DELETE /vdisks/{vdiskid}
// Delete Vdisk
func (api VdisksAPI) DeleteVdisk(w http.ResponseWriter, r *http.Request) {

	vars := mux.Vars(r)
	vdiskID := vars["vdiskid"]

	_, resp, err := api.AysAPI.Ays.GetServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)

	if err != nil {
		log.Errorf("error executing blueprint for vdisk %s deletion : %+v", vdiskID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if resp.StatusCode == http.StatusNotFound {
		tools.WriteError(w, http.StatusNotFound, fmt.Errorf("A vdisk with ID %s does not exist", vdiskID))
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

	run, err := tools.ExecuteBlueprint(api.AysRepo, "vdisk", vdiskID, "delete", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for vdisk deletion : %+v", err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if err = tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err)
		}
		return
	}

	_, err = api.AysAPI.Ays.DeleteServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)

	if err != nil {
		log.Errorf("Error in deleting vdisk %s : %+v", vdiskID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
