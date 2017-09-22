package healthcheck

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListStorageClusterHealth is the handler for GET /health/storageclusters/{storageclusterid}
// List NodeHealth
func (api *HealthCheckApi) ListStorageClusterHealth(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	storageClusterID := vars["storageclusterid"]

	serviceName := fmt.Sprintf("storage_cluster_%s", storageClusterID)
	service, res, err := aysClient.Ays.GetServiceByName(serviceName, "healthcheck", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, "listing storage cluster health checks") {
		return
	}
	var respBody struct {
		HealthChecks []HealthCheck `json:"healthchecks" validate:"nonzero"`
	}
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	if respBody.HealthChecks == nil {
		respBody.HealthChecks = make([]HealthCheck, 0)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
