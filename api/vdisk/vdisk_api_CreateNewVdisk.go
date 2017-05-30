package vdisk

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"

	"github.com/zero-os/0-rest-api/api/tools"
)

// CreateNewVdisk is the handler for POST /vdisks
// Create a new vdisk, can be a copy from an existing vdisk
func (api VdisksAPI) CreateNewVdisk(w http.ResponseWriter, r *http.Request) {
	var reqBody VdiskCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	_, resp, err := api.AysAPI.Ays.GetServiceByName(reqBody.ID, "vdisk", api.AysRepo, nil, nil)
	if err != nil {
		log.Errorf("error getting vdisk service by name : %+v", reqBody.ID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	if resp.StatusCode != http.StatusNotFound {
		tools.WriteError(w, http.StatusConflict, fmt.Errorf("A vdisk with ID %s already exists", reqBody.ID))
		return
	}

	_, resp, err = api.AysAPI.Ays.GetServiceByName(reqBody.Storagecluster, "storage_cluster", api.AysRepo, nil, nil)
	if err != nil {
		log.Errorf("error getting storage cluster service by name : %+v", reqBody.Storagecluster, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	if resp.StatusCode == http.StatusNotFound {
		tools.WriteError(w, http.StatusBadRequest, fmt.Errorf("Storagecluster with name %s doesn't exists", reqBody.Storagecluster))
		return
	}

	// Create the blueprint
	bp := struct {
		Size           int    `yaml:"size" json:"size"`
		BlockSize      int    `yaml:"blocksize" json:"blocksize"`
		TemplateVdisk  string `yaml:"templateVdisk" json:"templateVdisk"`
		ReadOnly       bool   `yaml:"readOnly" json:"readOnly"`
		Type           string `yaml:"type" json:"type"`
		StorageCluster string `yaml:"storageCluster" json:"storageCluster"`
	}{
		Size:           reqBody.Size,
		BlockSize:      reqBody.Blocksize,
		TemplateVdisk:  reqBody.Templatevdisk,
		ReadOnly:       reqBody.ReadOnly,
		Type:           string(reqBody.Vdisktype),
		StorageCluster: reqBody.Storagecluster,
	}

	bpName := fmt.Sprintf("vdisk__%s", reqBody.ID)

	obj := make(map[string]interface{})
	obj[bpName] = bp
	obj["actions"] = []tools.ActionBlock{{Action: "install", Service: reqBody.ID, Actor: "vdisk"}}

	// And Execute
	if _, err := tools.ExecuteBlueprint(api.AysRepo, "vdisk", reqBody.ID, "install", obj); err != nil {
		log.Errorf("error executing blueprint for vdisk %s creation : %+v", reqBody.ID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/vdisks/%s", reqBody.ID))
	w.WriteHeader(http.StatusCreated)
}
