package healthcheck

import (
	"encoding/json"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListNodesHealth is the handler for GET /health/nodes
// List NodesHealth
func (api HealthCheckApi) ListNodesHealth(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	queryParams := map[string]interface{}{
		"fields": "hostname,id,healthchecks",
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
		for _, healthcheck := range node.HealthChecks {
			if healthcheck.Status != "OK" {
				healthstatus = healthcheck.Status
				if healthcheck.Status == "ERROR" {
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
