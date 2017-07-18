package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListDashboards is the handler for GET /nodes/{nodeid}/dashboards
// List running Dashboards
func (api NodeAPI) ListDashboards(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	graphId := vars["graphid"]

	query := map[string]interface{}{
		"parent": fmt.Sprintf("grafana!%s", graphId),
		"fields": "slug",
	}
	services, res, err := aysClient.Ays.ListServicesByRole("dashboard", api.AysRepo, nil, query)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error getting dashboard services from ays")
		return
	}
	if res.StatusCode != http.StatusOK {
		w.WriteHeader(res.StatusCode)
		return
	}

	type dashboardItem struct {
		Slug string `json:"slug" validate:"nonzero"`
	}

	var respBody = make([]DashboardListItem, len(services))
	for i, service := range services {
		var data dashboardItem
		if err := json.Unmarshal(service.Data, &data); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
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
