package graph

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteDashboard is the handler for DELETE /graph/{graphid}/dashboard/{dashboardname}
// Remove dashboard
func (api *GraphAPI) DeleteDashboard(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	dashboard := vars["dashboardname"]

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "uninstall",
			Actor:   "dashboard",
			Service: dashboard,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "dashboard", dashboard, "delete", blueprint)
	errmsg := "Error executing blueprint for dashboard deletion "
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for dashboard deletion")
		}
		return
	}

	res, err := aysClient.Ays.DeleteServiceByName(dashboard, "dashboard", api.AysRepo, nil, nil)
	if !tools.HandleAYSDeleteResponse(err, res, w, "deleting dashboard") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
