package storagecluster

import (
	"encoding/json"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListAllClusters is the handler for GET /storageclusters
// List all running clusters
func (api *StorageclustersAPI) ListAllClusters(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	respBody := []string{}

	for _, role := range []string{"block_cluster", "object_cluster"} {
		clusters, err := getClusters(aysClient, api.AysRepo, role)
		if err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "")
			return
		}

		respBody = append(respBody, clusters...)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}

func getClusters(aysClient *tools.AYStool, aysRepo string, role string) ([]string, error) {
	respBody := []string{}

	type Data struct {
		Label string `json:"label"`
	}

	query := map[string]interface{}{
		"fields": "label",
	}
	services, _, err := aysClient.Ays.ListServicesByRole(role, aysRepo, nil, query)

	if err != nil {
		return nil, err
	}

	for _, service := range services {
		data := Data{}
		if err := json.Unmarshal(service.Data, &data); err != nil {
			return nil, err
		}
		respBody = append(respBody, data.Label)
	}
	return respBody, nil
}
