package vdiskstorage

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ImportImage is the handler for POST /vdiskstorage/{vdiskstorageid}/images
// Import an image from an FTP server into the VdiskStorage
func (api *VdiskstorageAPI) ImportImage(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	var imageImport ImageImport
	vdiskStorageID := mux.Vars(r)["vdiskstorageid"]

	// make sure the vdiskstorage exists
	exists, err := aysClient.ServiceExists("vdiskstorage", vdiskStorageID, api.AysRepo)
	if err != nil {
		errmsg := fmt.Sprintf("error getting image vdiskstorage by name %s", vdiskStorageID)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	if !exists {
		err := fmt.Errorf("vdiskstorage %s not found", vdiskStorageID)
		tools.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}

	// decode request
	defer r.Body.Close()
	if err := json.NewDecoder(r.Body).Decode(&imageImport); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := imageImport.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// check for duplicate
	if !imageImport.Overwrite {
		exists, err = aysClient.ServiceExists("vdisk_image", imageImport.Name, api.AysRepo)
		if err != nil {
			errmsg := fmt.Sprintf("error getting image service by name %s ", imageImport.Name)
			tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
			return
		}
		if exists {
			tools.WriteError(w, http.StatusConflict, fmt.Errorf("A vdisk with ID %s already exists", imageImport.Name), "")
			return
		}
	}

	// execute blueprint
	bp := make(map[string]interface{})
	bp[fmt.Sprintf("vdisk_image__%s", imageImport.Name)] = map[string]interface{}{
		"ftpURL":         imageImport.URL,
		"diskBlockSize":  imageImport.DiskBlockSize,
		"vdiskstorage":   vdiskStorageID,
		"exportName":     imageImport.ExportName,
		"exportSnapshot": imageImport.ExportSnapshot,
		"encryptionKey":  imageImport.EncryptionKey,
		"overwrite":      imageImport.Overwrite,
	}
	bp["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "vdisk_image",
		Service: imageImport.Name,
	}}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk_image", imageImport.Name, "install", bp)
	if !tools.HandleExecuteBlueprintResponse(err, w, fmt.Sprintf("error executing blueprint for image import")) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}

	var respBody Image
	service, response, err := aysClient.Ays.GetServiceByName(imageImport.Name, "vdisk_image", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, response, w, fmt.Sprintf("getting service %s", imageImport.Name)) {
		return
	}
	respBody.Name = imageImport.Name

	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/vdiskstorage/%s/images/%s", vdiskStorageID, imageImport.Name))
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(&respBody)
}
