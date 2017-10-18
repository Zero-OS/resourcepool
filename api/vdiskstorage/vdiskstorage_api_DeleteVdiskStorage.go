package vdiskstorage

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteVdiskStorage is the handler for DELETE /vdiskstorage/{vdiskstorageid}
// DeleteVdiskStorage deletes VdiskStorage
func (api *VdiskstorageAPI) DeleteVdiskStorage(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}

	vdiskstorageID := mux.Vars(r)["vdiskstorageid"]

	query := map[string]interface{}{
		"parent": fmt.Sprintf("vdiskstorage!%s", vdiskstorageID),
	}
	services, resp, err := aysClient.Ays.ListServicesByRole("vdisk", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, resp, w, "listing vdisks") {
		return
	}

	if len(services) > 0 {
		err = fmt.Errorf("Deleting a vdisk storage that consume vdisks is not allowed")
		tools.WriteError(w, http.StatusBadRequest, err, "")
	}

	services, resp, err = aysClient.Ays.ListServicesByRole("vdisk_image", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, resp, w, "listing vdisk images") {
		return
	}

	if len(services) > 0 {
		err = fmt.Errorf("Deleting a vdisk storage that consume vdisk images is not allowed")
		tools.WriteError(w, http.StatusBadRequest, err, "")
	}

	res, err := aysClient.Ays.DeleteServiceByName(vdiskstorageID, "vdiskstorage", api.AysRepo, nil, nil)
	if !tools.HandleAYSDeleteResponse(err, res, w, "deleting vdiskstorage") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
