package vdiskstorage

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

func (api VdiskstorageAPI) ListVdiskStorages(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vdiskstorages := []CreateVdiskStorage{}

	queryParams := map[string]interface{}{"fields": "blockCluster,slaveCluster,objectCluster"}
	services, res, err := aysClient.Ays.ListServicesByRole("vdiskstorage", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "listing vdiskstorage health checks") {
		return
	}

	for _, service := range services {
		var data CreateVdiskStorage
		if err := json.Unmarshal(service.Data, &data); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}
		vdiskstorages = append(vdiskstorages, data)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&vdiskstorages)

}
