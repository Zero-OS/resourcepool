package graph

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// UpdateGraph is the handler for POST /graphs/{graphid}
// Update Graph
func (api *GraphAPI) UpdateGraph(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody Graph
	vars := mux.Vars(r)
	graphid := vars["graphid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	if _, err := api.client.IsServiceExists("grafana", graphid); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// _, res, err := aysClient.Ays.GetServiceByName(graphid, "grafana", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "Getting grafana service") {
	// 	return
	// }
	// obj := make(map[string]interface{})
	bp := ays.Blueprint{
		fmt.Sprintf("grafana__%s", graphid): reqBody,
	}
	bpName := ays.BlueprintName("grafana", graphid, "update")

	// if err := api.client.CreateBlueprint(bpName, bp); err != nil {
	// 	err.Handle(w, http.StatusInternalServerError)
	// 	return
	// }

	// // var processJobs ays.ProcessChangeJobs
	// processJobs, err := api.client.ExecuteBlueprint(bpName)
	// if err != nil {
	// 	if ayserr, ok := err.(*ays.Error); ok {
	// 		ayserr.Handle(w, http.StatusInternalServerError)
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
	// 	}
	// 	return
	// }

	// if err := processJobs.Wait(); err != nil {
	// 	if ayserr, ok := err.(*ays.Error); ok {
	// 		ayserr.Handle(w, http.StatusInternalServerError)
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
	// 	}
	// 	return
	// }

	if err := api.client.CreateExec(bpName, bp); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
