package vdisk

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// GetVdiskInfo is the handler for GET /vdisks/{vdiskid}
// Get vdisk information
func (api VdisksAPI) GetVdiskInfo(w http.ResponseWriter, r *http.Request) {
	vdiskID := mux.Vars(r)["vdiskid"]

	serv, resp, err := api.AysAPI.Ays.GetServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("getting info about vdisk %s", vdiskID)) {
		return
	}

	var respBody Vdisk
	if err := json.Unmarshal(serv.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	respBody.ID = serv.Name

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
