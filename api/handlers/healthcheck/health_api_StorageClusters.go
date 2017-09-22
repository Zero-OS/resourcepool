package healthcheck

import (
	"encoding/json"
	"fmt"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ListStorageClustersHealth is the handler for GET /health/storageclusters
// List StorageClustersHealth
func (api *HealthCheckApi) ListStorageClustersHealth(w http.ResponseWriter, r *http.Request) {
	services, err := api.client.ListServices("storage_cluster", ays.ListServiceOpt{
		Fields: []string{"label", "clusterType"},
	})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	var respBody []StorageClusterHealthCheck
	for _, service := range services {
		var cluster StorageCluster
		if err := json.Unmarshal(service.Data, &cluster); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		if cluster.ClusterType == "tlog" {
			continue
		}

		data := StorageClusterHealthCheck{
			Label:  service.Name,
			Status: "OK",
		}

		// Get healthcheck data
		serviceName := fmt.Sprintf("storage_cluster_%s", service.Name)
		healthService, err := api.client.GetService("healthcheck", serviceName, "", nil)
		if err != nil {
			handlers.HandleError(w, err)
			return
		}

		var healthcheck HealthCheck
		if err := json.Unmarshal(healthService.Data, &healthcheck); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		for _, message := range healthcheck.Messages {
			if message.Status != "OK" {
				data.Status = message.Status
				if message.Status == "ERROR" {
					break
				}
			}
		}
		respBody = append(respBody, data)

	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
