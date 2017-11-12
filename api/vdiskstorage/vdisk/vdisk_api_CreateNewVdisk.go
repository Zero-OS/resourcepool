package vdisk

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	tools "github.com/zero-os/0-orchestrator/api/tools"
)

// CreateNewVdisk is the handler for POST /vdisks
// Create a new vdisk, can be a copy from an existing vdisk
func (api *VdisksAPI) CreateNewVdisk(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	var reqBody VdiskCreate
	vars := mux.Vars(r)
	vdiskStoreID := vars["vdiskstorageid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// get vdiskstorage

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	exists, err := aysClient.ServiceExists("vdisk", reqBody.ID, api.AysRepo)
	if err != nil {
		errmsg := fmt.Sprintf("error getting vdisk service by name %s ", reqBody.ID)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	if exists {
		tools.WriteError(w, http.StatusConflict, fmt.Errorf("A vdisk with ID %s already exists", reqBody.ID), "")
		return
	}

	// Check if disk size is larger than the image
	var image struct {
		Size uint64 `json:"size" validate:"nonzero"`
	}
	service, response, err := aysClient.Ays.GetServiceByName(reqBody.ImageID, "vdisk_image", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, response, w, fmt.Sprintf("getting service %s", reqBody.ImageID)) {
		return
	}
	if err := json.Unmarshal(service.Data, &image); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}
	if reqBody.Size < image.Size {
		err = fmt.Errorf("Vdisk size should be larger than the image size")
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// Create the blueprint
	bp := struct {
		Size         uint64 `yaml:"size" json:"size"`
		BlockSize    int    `yaml:"blocksize" json:"blocksize"`
		ImageID      string `yaml:"imageId" json:"imageId"`
		ReadOnly     bool   `yaml:"readOnly" json:"readOnly"`
		Type         string `yaml:"type" json:"type"`
		VdiskStorage string `yaml:"vdiskstorage" json:"vdiskstorage"`
	}{
		Size:         reqBody.Size,
		BlockSize:    reqBody.Blocksize,
		ImageID:      reqBody.ImageID,
		ReadOnly:     reqBody.ReadOnly,
		Type:         string(reqBody.Vdisktype),
		VdiskStorage: vdiskStoreID,
	}

	bpName := fmt.Sprintf("vdisk__%s", reqBody.ID)

	obj := make(map[string]interface{})
	obj[bpName] = bp
	obj["actions"] = []tools.ActionBlock{{Action: "install", Service: reqBody.ID, Actor: "vdisk"}}

	// And Execute

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", reqBody.ID, "install", obj)
	errmsg := fmt.Sprintf("error executing blueprint for vdisk %s creation", reqBody.ID)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}
	w.Header().Set("Location", fmt.Sprintf("/vdisks/%s", reqBody.ID))
	w.WriteHeader(http.StatusCreated)
}
