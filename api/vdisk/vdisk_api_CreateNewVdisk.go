package vdisk

import (
	"encoding/json"
	"fmt"

	"net/http"

	runs "github.com/zero-os/0-orchestrator/api/run"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateNewVdisk is the handler for POST /vdisks
// Create a new vdisk, can be a copy from an existing vdisk
func (api VdisksAPI) CreateNewVdisk(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody VdiskCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

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

	exists, err = aysClient.ServiceExists("storage_cluster", reqBody.Storagecluster, api.AysRepo)
	if err != nil {
		errmsg := fmt.Sprintf("error getting storage cluster service by name %s", reqBody.Storagecluster)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	if !exists {
		tools.WriteError(w, http.StatusBadRequest, fmt.Errorf("Storagecluster with name %s doesn't exists", reqBody.Storagecluster), "")
		return
	}

	// Create the blueprint
	bp := struct {
		Size               int    `yaml:"size" json:"size"`
		BlockSize          int    `yaml:"blocksize" json:"blocksize"`
		TemplateVdisk      string `yaml:"templateVdisk" json:"templateVdisk"`
		ReadOnly           bool   `yaml:"readOnly" json:"readOnly"`
		Type               string `yaml:"type" json:"type"`
		StorageCluster     string `yaml:"storageCluster" json:"storageCluster"`
		TlogStoragecluster string `yaml:"tlogStoragecluster" json:"tlogStoragecluster"`
	}{
		Size:               reqBody.Size,
		BlockSize:          reqBody.Blocksize,
		TemplateVdisk:      reqBody.Templatevdisk,
		ReadOnly:           reqBody.ReadOnly,
		Type:               string(reqBody.Vdisktype),
		StorageCluster:     reqBody.Storagecluster,
		TlogStoragecluster: reqBody.TlogStoragecluster,
	}

	bpName := fmt.Sprintf("vdisk__%s", reqBody.ID)

	obj := make(map[string]interface{})
	obj[bpName] = bp
	obj["actions"] = []tools.ActionBlock{{Action: "install", Service: reqBody.ID, Actor: "vdisk"}}

	// And Execute

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", reqBody.ID, "install", obj)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for vdisk %s creation", reqBody.ID)
		if httpErr.Resp.StatusCode/100 == 4 {
			tools.WriteError(w, httpErr.Resp.StatusCode, err, err.Error())
			return
		}
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	response := runs.Run{Runid: run.Key, State: runs.EnumRunState(run.State)}

	w.Header().Set("Location", fmt.Sprintf("/vdisks/%s", reqBody.ID))
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(&response)
}
