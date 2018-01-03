package healthcheck

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListNodesHealth is the handler for GET /health/nodes
// List NodesHealth
func (api *HealthCheckApi) ListNodesHealth(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
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
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
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

		var health struct {
			HealthChecks []HealthCheck `json:"healthchecks" validate:"nonzero"`
		}
		if err := json.Unmarshal(healthService.Data, &health); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		var messages int
		var skipped int

	HealthChecks:
		for _, healthCheck := range health.HealthChecks {
			messages += len(healthCheck.Messages)
			for _, message := range healthCheck.Messages {
				if message.Status == "SKIPPED" {
					skipped += 1
				} else if message.Status != "OK" {
					healthstatus = message.Status
					if message.Status == "ERROR" {
						break HealthChecks
					}
				}
			}
		}

		if skipped == messages {
			// Only set status to skipped if all messages have a skipped status
			respBody[i].Status = "SKIPPED"
		} else {
			respBody[i].Status = healthstatus

		}

	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
