package healthcheck

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListStorageClustersHealth is the handler for GET /health/storageclusters
// List StorageClustersHealth
func (api *HealthCheckApi) ListStorageClustersHealth(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	queryParams := map[string]interface{}{
		"fields": "label,clusterType",
	}
	services, res, err := aysClient.Ays.ListServicesByRole("storage_cluster", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "listing storagecluster health checks") {
		return
	}

	var respBody []StorageClusterHealthCheck
	for _, service := range services {
		var cluster StorageCluster
		if err := json.Unmarshal(service.Data, &cluster); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
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
		healthService, res, err := aysClient.Ays.GetServiceByName(serviceName, "healthcheck", api.AysRepo, nil, nil)
		if !tools.HandleAYSResponse(err, res, w, "listing storage clusters health checks") {
			return
		}

		var healthcheck HealthCheck
		if err := json.Unmarshal(healthService.Data, &healthcheck); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
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
