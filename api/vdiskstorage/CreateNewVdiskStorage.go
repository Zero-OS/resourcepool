package vdiskstorage

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// Creates the VM
func (api *VdiskstorageAPI) CreateNewVdiskStorage(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody VdiskStorage

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate vdiskstorage name
	if exists, err := aysClient.ServiceExists("vdiskstorage", reqBody.ID, api.AysRepo); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking vdiskstorage service exists")
		return
	} else if exists {
		err = fmt.Errorf("vdiskstorage with name %s does  exists", reqBody.ID)
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate block cluster name
	_, response, err := aysClient.Ays.GetServiceByName(reqBody.BlockCluster, "storage_cluster", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, response, w, fmt.Sprintf("getting service %s", reqBody.BlockCluster)) {
		return
	}

	// validate object cluster name
	_, response, err = aysClient.Ays.GetServiceByName(reqBody.ObjectCluster, "storage_cluster", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, response, w, fmt.Sprintf("getting service %s", reqBody.ObjectCluster)) {
		return
	}

	// validate slave cluster name
	_, response, err = aysClient.Ays.GetServiceByName(reqBody.SlaveCluster, "storage_cluster", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, response, w, fmt.Sprintf("getting service %s", reqBody.SlaveCluster)) {
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
