package vdisk

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListVdisks is the handler for GET /vdisks
// Get vdisk information
func (api *VdisksAPI) ListVdisks(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vdiskID := mux.Vars(r)["vdiskid"]
	queryParams := map[string]interface{}{
		"fields": "vdiskstorage,type",
	}

	services, resp, err := aysClient.Ays.ListServicesByRole("vdisk", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("Listing vdisk services %s", vdiskID)) {
		return
	}

	var respBody = make([]VdiskListItem, len(services))
	for idx, service := range services {
		var vdiskInfo VdiskListItem
		if err := json.Unmarshal(service.Data, &vdiskInfo); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
			return
		}
		vdiskInfo.ID = service.Name
		respBody[idx] = vdiskInfo
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
