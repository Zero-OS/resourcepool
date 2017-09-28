package vdiskstorage

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteImage is the handler for DELETE /vdiskstorage/{vdiskstorageid}/images/{imageid}
// Delete an vdisk image from the VdiskStorage
func (api *VdiskstorageAPI) DeleteImage(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	imageID := vars["imageid"]

	exists, err := aysClient.ServiceExists("vdisk_image", imageID, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to check for the image")
		return
	}

	if !exists {
		err = fmt.Errorf("image %s doesn't exist", imageID)
		tools.WriteError(w, http.StatusNotFound, err, err.Error())
		return
	}

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

	_, err = aysClient.Ays.DeleteServiceByName(imageID, "vdisk_image", api.AysRepo, nil, nil)

	if err != nil {
		errmsg := fmt.Sprintf("Error in deleting image %s ", imageID)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
