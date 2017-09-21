package graph

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetDashboard is the handler for GET /graph/{graphid}/dashboards/{dashboardname}
// Get Dashboard
func (api *GraphAPI) GetDashboard(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	graphId := vars["graphid"]
	name := vars["dashboardname"]

	dashboardService, err := api.client.GetService("dashboard", name, fmt.Sprintf("grafana!%s", graphId), []string{"dashboard", "slug", "grafana"})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}

	type dashboardItem struct {
		Dashboard string `json:"dashboard" validate:"nonzero"`
		Slug      string `json:"slug" validate:"nonzero"`
		Grafana   string `json:"grafana" validate:"nonzero"`
	}

	var data dashboardItem
	if err := json.Unmarshal(dashboardService.Data, &data); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	grafanaService, err := api.client.GetService("grafana", data.Grafana, "", []string{"node", "port"})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// query = map[string]interface{}{
	// 	"fields": "node,port",
	// }

	// service, res, err = aysClient.Ays.GetServiceByName(data.Grafana, "grafana", api.AysRepo, nil, query)
	// if err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting dashboard service from ays")
	// 	return
	// }
	// if res.StatusCode != http.StatusOK {
	// 	w.WriteHeader(res.StatusCode)
	// 	return
	// }

	type grafanaItem struct {
		Node string `json:"node" validate:"nonzero"`
		Port int    `json:"port" validate:"nonzero"`
	}

	var grafana grafanaItem
	if err := json.Unmarshal(grafanaService.Data, &grafana); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}
	nodeService, err := api.client.GetService("node.zero-os", grafana.Node, "", []string{"RedisAddr"})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// query = map[string]interface{}{
	// 	"fields": "RedisAddr",
	// }
	// serviceNode, res, err := aysClient.Ays.GetServiceByName(grafana.Node, "node.zero-os", api.AysRepo, nil, query)
	// if err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting node service from ays")
	// 	return
	// }
	// if res.StatusCode != http.StatusOK {
	// 	w.WriteHeader(res.StatusCode)
	// 	return
	// }

	type nodeItem struct {
		RedisAddr string `json:"RedisAddr" validate:"nonzero"`
	}

	var node nodeItem
	if err := json.Unmarshal(nodeService.Data, &node); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	var respBody DashboardListItem
	dashboard := DashboardListItem{
		Name:      dashboardService.Name,
		Slug:      data.Slug,
		Dashboard: data.Dashboard,
		Url:       fmt.Sprintf("http://%s:%d/dashboard/db/%s", node.RedisAddr, grafana.Port, data.Slug),
	}
	respBody = dashboard

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
