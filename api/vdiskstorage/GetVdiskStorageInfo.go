package vdiskstorage

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

func (api *VdiskstorageAPI) GetVdiskStorageInfo(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var respBody VdiskStorage

	// validate vdiskstorage name
	vars := mux.Vars(r)
	vdiskstorageid := vars["vdiskstorageid"]

	service, response, err := aysClient.Ays.GetServiceByName(vdiskstorageid, "vdiskstorage", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, response, w, fmt.Sprintf("getting service %s", vdiskstorageid)) {
		return
	}

	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}
	respBody.ID = vdiskstorageid
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
