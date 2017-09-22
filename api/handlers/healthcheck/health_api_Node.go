package healthcheck

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ListNodeHealth is the handler for GET /health/nodes/{nodeid}
// List NodeHealth
func (api *HealthCheckApi) ListNodeHealth(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	serviceName := fmt.Sprintf("node_%s", nodeID)
	service, err := api.client.GetService("healthcheck", serviceName, "", nil)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	// // service, res, err := aysClient.Ays.GetServiceByName(serviceName, "healthcheck", api.AysRepo, nil, nil)

	// if !tools.HandleAYSResponse(err, res, w, "listing nodes health checks") {
	// 	return
	// }
	var respBody struct {
		HealthChecks []HealthCheck `json:"healthchecks" validate:"nonzero"`
	}
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
