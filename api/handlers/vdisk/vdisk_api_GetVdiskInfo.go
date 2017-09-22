package vdisk

import (
	"encoding/json"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetVdiskInfo is the handler for GET /vdisks/{vdiskid}
// Get vdisk information
func (api *VdisksAPI) GetVdiskInfo(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vdiskID := mux.Vars(r)["vdiskid"]

	serv, err := api.client.GetService("vdisk", vdiskID, "", []string{})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// serv, resp, err := aysClient.Ays.GetServiceByName(vdiskID, "vdisk", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("getting info about vdisk %s", vdiskID)) {
	// 	return
	// }

	var respBody Vdisk
	if err := json.Unmarshal(serv.Data, &respBody); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling response body")
		return
	}
	respBody.ID = serv.Name

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
