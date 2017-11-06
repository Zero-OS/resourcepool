package graph

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetDashboard is the handler for GET /graph/{graphid}/dashboards/{dashboardname}
// Get Dashboard
func (api *GraphAPI) GetDashboard(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	graphID := vars["graphid"]
	name := vars["dashboardname"]

	query := map[string]interface{}{
		"fields": "node,port,url",
	}
	service, res, err := aysClient.Ays.GetServiceByName(graphID, "grafana", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, res, w, "Get grafana service by name") {
		return
	}

	var grafana GraphService
	if err := json.Unmarshal(service.Data, &grafana); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	query = map[string]interface{}{
		"fields": "dashboard,slug,grafana",
	}
	service, res, err = aysClient.Ays.GetServiceByName(name, "dashboard", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, res, w, "Get dashboard by name") {
		return
	}

	if service.Parent.Name != graphID {
		err := fmt.Errorf("dashboard %s does not exists under parent %s", name, graphID)
		tools.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	type dashboardItem struct {
		Dashboard string `json:"dashboard" validate:"nonzero"`
		Slug      string `json:"slug" validate:"nonzero"`
		Grafana   string `json:"grafana" validate:"nonzero"`
	}

	var data dashboardItem
	if err := json.Unmarshal(service.Data, &data); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	query = map[string]interface{}{
		"fields": "redisAddr",
	}
	serviceNode, res, err := aysClient.Ays.GetServiceByName(grafana.Node, "node.zero-os", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, res, w, "Get node by name") {
		return
	}

	type nodeItem struct {
		RedisAddr string `json:"RedisAddr" validate:"nonzero"`
	}

	var node nodeItem
	if err := json.Unmarshal(serviceNode.Data, &node); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	var url string
	if grafana.URL != "" {
		url = grafana.URL
	} else {
		url = fmt.Sprintf("http://%s:%d", node.RedisAddr, grafana.Port)
	}

	var respBody DashboardListItem
	dashboard := DashboardListItem{
		Name:      name,
		Slug:      data.Slug,
		Dashboard: data.Dashboard,
		Url:       fmt.Sprintf("%s/dashboard/db/%s", url, data.Slug),
	}
	respBody = dashboard

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
