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

// CreateDashboard is the handler for POST /graph/{graphid}/dashboards
// Creates a new dashboard
func (api *GraphAPI) CreateDashboard(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody Dashboard
	vars := mux.Vars(r)
	graphId := vars["graphid"]

	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	exists, err := api.client.IsServiceExists("dashboard", reqBody.Name)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	if exists {
		err := fmt.Errorf("Dashboard with the name %s does exist", reqBody.Name)
		httperror.WriteError(w, http.StatusConflict, err, err.Error())
		return
	}
	// Create blueprint
	// bp := struct {
	// 	Dashboard string `json:"dashboard" yaml:"dashboard"`
	// 	Grafana   string `json:"grafana" yaml:"grafana"`
	// }{
	// 	Dashboard: reqBody.Dashboard,
	// 	Grafana:   graphId,
	// }
	bp := ays.Blueprint{
		"dashboard": reqBody.Dashboard,
		"grafana":   graphId,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("dashboard__%s", reqBody.Name)] = bp
	obj["actions"] = []ays.ActionBlock{{
		Action:  "install",
		Actor:   "dashboard",
		Service: reqBody.Name}}

	bpName := ays.BlueprintName("dashboard", reqBody.Name, "install")
	_, err = api.client.CreateExecRun(bpName, obj, true)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "dashboard", reqBody.Name, "install", obj)
	// errmsg := fmt.Sprintf("error executing blueprint for dashboard %s creation", reqBody.Name)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }
	w.Header().Set("Location", fmt.Sprintf("/graphs/%s/dashboards/%s", graphId, reqBody.Name))
	w.WriteHeader(http.StatusCreated)
}
