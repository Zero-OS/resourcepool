package vdiskstorage

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteImage is the handler for DELETE /vdiskstorage/{vdiskstorageid}/images/{imageid}
// Delete an vdisk image from the VdiskStorage
func (api *VdiskstorageAPI) DeleteImage(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	imageID := vars["imageid"]

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "delete",
			Actor:   "vdisk_image",
			Service: imageID,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk_image", imageID, "delete", blueprint)
	if !tools.HandleExecuteBlueprintResponse(err, w, "Error executing blueprint for image deletion ") {
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for image deletion")
		}
		return
	}

	res, err := aysClient.Ays.DeleteServiceByName(imageID, "vdisk_image", api.AysRepo, nil, nil)
	if !tools.HandleAYSDeleteResponse(err, res, w, "deleting vdisk_image") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
