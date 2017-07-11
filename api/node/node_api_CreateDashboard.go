package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	tools "github.com/zero-os/0-orchestrator/api/tools"
)

// CreateDashboard is the handler for POST /graph/{graphid}/dashboards
// Creates a new dashboard
func (api NodeAPI) CreateDashboard(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody Dashboard
	vars := mux.Vars(r)
	graphId := vars["graphid"]

	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// Create blueprint
	bp := struct {
		Dashboard string `json:"dashboard" yaml:"dashboard"`
		Grafana   string `json:"grafana" yaml:"grafana"`
	}{
		Dashboard: reqBody.Dashboard,
		Grafana:   graphId,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("dashboard__%s", reqBody.Name)] = bp
	obj["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "dashboard",
		Service: reqBody.Name}}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "dashboard", reqBody.Name, "install", obj)
	errmsg := fmt.Sprintf("error executing blueprint for dashboard %s creation", reqBody.Name)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}
	w.Header().Set("Location", fmt.Sprintf("/graphs/%s/dashboards/%s", graphId, reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
