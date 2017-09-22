package vdisk

import (
	"encoding/json"
	"fmt"

	"github.com/zero-os/0-orchestrator/api/ays"

	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// CreateNewVdisk is the handler for POST /vdisks
// Create a new vdisk, can be a copy from an existing vdisk
func (api *VdisksAPI) CreateNewVdisk(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody VdiskCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}
	log.Debugf("%+v", reqBody)

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	exists, err := api.client.IsServiceExists("vdisk", reqBody.ID)
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// exists, err := aysClient.ServiceExists("vdisk", reqBody.ID, api.AysRepo)
	// if err != nil {
	// 	errmsg := fmt.Sprintf("error getting vdisk service by name %s ", reqBody.ID)
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	return
	// }
	if exists {
		httperror.WriteError(w, http.StatusConflict, fmt.Errorf("A vdisk with ID %s already exists", reqBody.ID), "")
		return
	}

	exists, err = api.client.IsServiceExists("storage_cluster", reqBody.BlockStoragecluster)
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
		// errmsg := fmt.Sprintf("error getting storage cluster service by name %s", reqBody.BlockStoragecluster)
		// httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
		// return
	}
	if !exists {
		httperror.WriteError(w, http.StatusBadRequest, fmt.Errorf("Storagecluster with name %s doesn't exists", reqBody.BlockStoragecluster), "")
		return
	}

	// Create the blueprint
	bp := struct {
		Size                 int    `yaml:"size" json:"size"`
		BlockSize            int    `yaml:"blocksize" json:"blocksize"`
		TemplateVdisk        string `yaml:"templateVdisk" json:"templateVdisk"`
		ReadOnly             bool   `yaml:"readOnly" json:"readOnly"`
		Type                 string `yaml:"type" json:"type"`
		BlockStoragecluster  string `yaml:"blockStoragecluster" json:"blockStoragecluster"`
		ObjectStoragecluster string `yaml:"objectStoragecluster" json:"objectStoragecluster"`
		BackupStoragecluster string `yaml:"backupStoragecluster" json:"backupStoragecluster"`
	}{
		Size:                 reqBody.Size,
		BlockSize:            reqBody.Blocksize,
		TemplateVdisk:        reqBody.Templatevdisk,
		ReadOnly:             reqBody.ReadOnly,
		Type:                 string(reqBody.Vdisktype),
		BlockStoragecluster:  reqBody.BlockStoragecluster,
		ObjectStoragecluster: reqBody.ObjectStoragecluster,
		BackupStoragecluster: reqBody.BackupStoragecluster,
	}

	bpName := fmt.Sprintf("vdisk__%s", reqBody.ID)

	obj := ays.Blueprint{
		bpName:    bp,
		"actions": []ays.ActionBlock{{Action: "install", Service: reqBody.ID, Actor: "vdisk"}},
	}
	// obj[bpName] = bp
	// obj["actions"] =

	// And Execute
	if _, err := api.client.CreateExecRun(bpName, obj, true); err != nil {
		if ayserr, ok := err.(*ays.Error); ok {
			ayserr.Handle(w, http.StatusInternalServerError)
		} else {
			httperror.WriteError(w, http.StatusInternalServerError, err, "fail to create vdisk")
		}
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", reqBody.ID, "install", obj)
	// errmsg := fmt.Sprintf("error executing blueprint for vdisk %s creation", reqBody.ID)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }
	w.Header().Set("Location", fmt.Sprintf("/vdisks/%s", reqBody.ID))
	w.WriteHeader(http.StatusCreated)
}
