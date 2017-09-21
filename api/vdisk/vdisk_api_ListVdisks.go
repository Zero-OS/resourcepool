package vdisk

import (
	"encoding/json"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/httperror"

	"net/http"
)

// ListVdisks is the handler for GET /vdisks
// Get vdisk information
func (api *VdisksAPI) ListVdisks(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	// vdiskID := mux.Vars(r)["vdiskid"]
	// queryParams := map[string]interface{}{
	// 	"fields": "blockStoragecluster,objectStoragecluster,backupStoragecluster,type",
	// }

	// services, resp, err := aysClient.Ays.ListServicesByRole("vdisk", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("Listing vdisk services %s", vdiskID)) {
	// 	return
	// }
	services, err := api.client.ListServices("vdisk", ays.ListServiceOpt{
		Fields: []string{"blockStoragecluster", "objectStoragecluster", "backupStoragecluster", "type"},
	})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}

	var respBody = make([]VdiskListItem, len(services))
	for idx, service := range services {
		var vdiskInfo VdiskListItem
		if err := json.Unmarshal(service.Data, &vdiskInfo); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
			return
		}
		vdiskInfo.ID = service.Name
		respBody[idx] = vdiskInfo
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
