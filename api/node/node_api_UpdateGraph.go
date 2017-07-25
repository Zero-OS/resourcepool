package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// UpdateGraph is the handler for POST /graphs/{graphid}
// Update Graph
func (api NodeAPI) UpdateGraph(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
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
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	_, res, err := aysClient.Ays.GetServiceByName(graphid, "grafana", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "Getting grafana service") {
		return
	}
	obj := make(map[string]interface{})
	obj[fmt.Sprintf("grafana__%s", graphid)] = reqBody

	_, err = aysClient.ExecuteBlueprint(api.AysRepo, "grafana", graphid, "update", obj)

	errmsg := fmt.Sprintf("error executing blueprint for grafana %s update", graphid)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	w.WriteHeader(http.StatusNoContent)

}
