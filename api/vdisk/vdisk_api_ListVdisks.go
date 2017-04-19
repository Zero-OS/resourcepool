package vdisk

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// ListVdisks is the handler for GET /vdisks
// Get vdisk information
func (api VdisksAPI) ListVdisks(w http.ResponseWriter, r *http.Request) {
	vdiskID := mux.Vars(r)["vdiskid"]

	services, resp, err := api.AysAPI.Ays.ListServicesByRole("vdisk", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("Listing vdisk services %s", vdiskID)) {
		return
	}

	var respBody = make([]VdiskListItem, len(services))
	for _, service := range services {
		var vdiskInfo VdiskListItem
		if err := json.Unmarshal(service.Data, &vdiskInfo); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err)
			return
		}
		vdiskInfo.ID = service.Name
		respBody = append(respBody, vdiskInfo)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
