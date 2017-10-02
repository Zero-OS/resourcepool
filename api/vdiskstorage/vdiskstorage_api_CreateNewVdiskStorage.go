package vdiskstorage

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// Creates the VM
func (api *VdiskstorageAPI) CreateNewVdiskStorage(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	var reqBody VdiskStorage

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(aysClient, api); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// check if service exists
	exists, err := aysClient.ServiceExists("vdiskstorage", reqBody.ID, api.AysRepo)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking vdiskstorage service exists")
		return
	}

	if exists {
		err = fmt.Errorf("vdiskstorage with name %s already exists", reqBody.ID)
		tools.WriteError(w, http.StatusConflict, err, "")
		return
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("vdiskstorage__%s", reqBody.ID)] = CreateVdiskStorage{
		BlockCluster:  reqBody.BlockCluster,
		ObjectCluster: reqBody.ObjectCluster,
		SlaveCluster:  reqBody.SlaveCluster,
	}

	_, err = aysClient.UpdateBlueprint(api.AysRepo, "vdiskstorage", reqBody.ID, "install", obj)
	if !tools.HandleExecuteBlueprintResponse(err, w, "") {
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/vdiskstorage/%s", reqBody.ID))
	w.WriteHeader(http.StatusCreated)
}
