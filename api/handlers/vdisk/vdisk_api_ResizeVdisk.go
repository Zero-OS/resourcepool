package vdisk

import (
	"encoding/json"
	"fmt"

	"github.com/zero-os/0-orchestrator/api/ays"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ResizeVdisk is the handler for POST /vdisks/{vdiskid}/resize
// Resize Vdisk
func (api *VdisksAPI) ResizeVdisk(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody VdiskResize

	vdiskID := mux.Vars(r)["vdiskid"]

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

	// srv, resp, err := aysClient.Ays.GetServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("getting info about vdisk %s", vdiskID)) {
	// 	return
	// }
	srv, err := api.client.GetService("vdisk", vdiskID, "", []string{})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}

	var vDisk Vdisk
	if err := json.Unmarshal(srv.Data, &vDisk); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
		return
	}

	if vDisk.Size > reqBody.NewSize {
		err := fmt.Errorf("newSize: %v is smaller than current size %v", reqBody.NewSize, vDisk.Size)
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// Create resize blueprint
	bp := struct {
		Size int `yaml:"size" json:"size"`
	}{
		Size: reqBody.NewSize,
	}

	decl := fmt.Sprintf("vdisk__%v", vdiskID)
	obj := ays.Blueprint{
		decl: bp,
	}
	// obj[decl] = bp

	// And execute
	bpName := ays.BlueprintName("vdisk", vdiskID, "resize")
	if err := api.client.CreateBlueprint(bpName, obj); err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}

	{
		procesChanges, err := api.client.ExecuteBlueprint(bpName)
		if err != nil {
			if ayserr, ok := err.(*ays.Error); ok {
				ayserr.Handle(w, http.StatusInternalServerError)
			} else {
				httperror.WriteError(w, http.StatusInternalServerError, err, "fail to create vdisk")
			}
			return
		}

		if err := procesChanges.Wait(); err != nil {
			if ayserr, ok := err.(*ays.Error); ok {
				ayserr.Handle(w, http.StatusInternalServerError)
			} else {
				httperror.WriteError(w, http.StatusInternalServerError, err, "fail to create vdisk")
			}
			return
		}
	}
	// _, err = aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", vdiskID, "resize", obj)

	// errmsg := fmt.Sprintf("error executing blueprint for vdisk %s resize", vdiskID)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	w.WriteHeader(http.StatusNoContent)
}
