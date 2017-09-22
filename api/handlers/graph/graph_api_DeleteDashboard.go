package graph

import (
	"net/http"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// DeleteDashboard is the handler for DELETE /graph/{graphid}/dashboard/{dashboardname}
// Remove dashboard
func (api *GraphAPI) DeleteDashboard(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	dashboard := vars["dashboardname"]

	exists, err := api.client.IsServiceExists("dashboard", dashboard)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to check for the dashboard")
		return
	}

	if !exists {
		err := fmt.Errorf("Dashboard %s doesn't exist", dashboard)
		httperror.WriteError(w, http.StatusNotFound, err, err.Error())
		return
	}

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []ays.ActionBlock{{
			Action:  "uninstall",
			Actor:   "dashboard",
			Service: dashboard,
			Force:   true,
		}},
	}

	{
		bpName := ays.BlueprintName("dashboard", dashboard, "delete")
		_, err := api.client.CreateExecRun(bpName, blueprint, true)
		if err != nil {
			handlers.HandleError(w, err)
			return
		}
	}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "dashboard", dashboard, "delete", blueprint)
	// errmsg := "Error executing blueprint for dashboard deletion "
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// // Wait for the delete job to be finshed before we delete the service
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for dashboard deletion")
	// 	}
	// 	return
	// }

	if err := api.client.DeleteService("dashboard", dashboard); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
