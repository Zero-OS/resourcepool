package healthcheck

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListNodesHealth is the handler for GET /health/nodes
// List NodesHealth
func (api *HealthCheckApi) ListNodesHealth(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	queryParams := map[string]interface{}{
		"fields": "hostname,id",
	}
	services, res, err := aysClient.Ays.ListServicesByRole("node.zero-os", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "listing nodes health checks") {
		return
	}

	var respBody = make([]NodeHealthCheck, len(services))
	for i, service := range services {
		var node Node
		if err := json.Unmarshal(service.Data, &node); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}
		respBody[i].ID = service.Name
		respBody[i].Hostname = node.Hostname
		healthstatus := "OK"

		// Get healthcheck data
		serviceName := fmt.Sprintf("node_%s", service.Name)
		healthService, res, err := aysClient.Ays.GetServiceByName(serviceName, "healthcheck", api.AysRepo, nil, nil)
		if !tools.HandleAYSResponse(err, res, w, "listing nodes health checks") {
			return
		}

		var healthcheck HealthCheck
		if err := json.Unmarshal(healthService.Data, &healthcheck); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		for _, message := range healthcheck.Messages {
			if message.Status != "OK" {
				healthstatus = message.Status
				if message.Status == "ERROR" {
					break
				}
			}
		}
		respBody[i].Status = healthstatus

	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
