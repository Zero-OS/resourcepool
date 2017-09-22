package storagecluster

import (
	"encoding/json"

	log "github.com/Sirupsen/logrus"
	"github.com/zero-os/0-orchestrator/api/ays"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ListAllClusters is the handler for GET /storageclusters
// List all running clusters
func (api *StorageclustersAPI) ListAllClusters(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	respBody := []string{}
	type data struct {
		Label string `json:"label"`
	}

	services, err := api.client.ListServices("storage_cluster", ays.ListServiceOpt{
		Fields: []string{"label"},
	})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	log.Debug("storage clusters", services)
	// query := map[string]interface{}{
	// 	"fields": "label",
	// }
	// services, res, err := aysClient.Ays.ListServicesByRole("storage_cluster", api.AysRepo, nil, query)
	// if err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error calling ays list service")
	// 	return
	// }
	// if res.StatusCode != http.StatusOK {
	// 	w.WriteHeader(res.StatusCode)
	// 	return
	// }

	for _, service := range services {
		Data := data{}
		if err := json.Unmarshal(service.Data, &Data); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
			return
		}
		respBody = append(respBody, Data.Label)
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
