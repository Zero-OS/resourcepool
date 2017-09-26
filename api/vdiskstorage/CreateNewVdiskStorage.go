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
	exists, err := aysClient.ServiceExists("vdiskstorage", reqBody.ID, api.AysRepo)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking vdiskstorage service exists")
		return
	}

	if exists {
		err = fmt.Errorf("vdiskstorage with name %s already exists", reqBody.ID)
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate block cluster name
	exists, err = aysClient.ServiceExists("storage_cluster", reqBody.BlockCluster, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking storage_cluster service exists")
		return
	}
	if !exists {
		err = fmt.Errorf("storage_cluster with name %s does not exists", reqBody.BlockCluster)
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate object cluster name
	if reqBody.ObjectCluster != "" {
		exists, err = aysClient.ServiceExists("storage_cluster", reqBody.ObjectCluster, api.AysRepo)
		if err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error checking storage_cluster service exists")
			return
		}
		if !exists {
			err = fmt.Errorf("storage_cluster with name %s does not exists", reqBody.ObjectCluster)
			tools.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
		if reqBody.SlaveCluster != "" {
			// validate slave cluster name
			exists, err = aysClient.ServiceExists("storage_cluster", reqBody.SlaveCluster, api.AysRepo)
			if err != nil {
				tools.WriteError(w, http.StatusInternalServerError, err, "Error checking storage_cluster service exists")
				return
			}
			if !exists {
				err = fmt.Errorf("storage_cluster with name %s does not exists", reqBody.SlaveCluster)
				tools.WriteError(w, http.StatusBadRequest, err, "")
				return
			}
		}
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
