package graph

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ListDashboards is the handler for GET /nodes/{nodeid}/dashboards
// List running Dashboards
func (api *GraphAPI) ListDashboards(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	graphId := vars["graphid"]

	services, err := api.client.ListServices("dashbaord", ays.ListServiceOpt{
		Parent: fmt.Sprintf("grafana!%s", graphId),
		Fields: []string{"slug"},
	})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	// query := map[string]interface{}{
	// 	"parent":
	// 	"fields": "slug",
	// }
	// services, res, err := aysClient.Ays.ListServicesByRole("dashboard", api.AysRepo, nil, query)
	// if err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting dashboard services from ays")
	// 	return
	// }
	// if res.StatusCode != http.StatusOK {
	// 	w.WriteHeader(res.StatusCode)
	// 	return
	// }

	type dashboardItem struct {
		Slug string `json:"slug" validate:"nonzero"`
	}

	var respBody = make([]DashboardListItem, len(services))
	for i, service := range services {
		var data dashboardItem
		if err := json.Unmarshal(service.Data, &data); err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
			return
		}

		dashboard := DashboardListItem{
			Name: service.Name,
			Slug: data.Slug,
		}
		respBody[i] = dashboard
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
