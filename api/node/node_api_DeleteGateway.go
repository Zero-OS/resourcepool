package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteGateway is the handler for DELETE /nodes/{nodeid}/gws/{gwname}
// Delete gateway instance
func (api *NodeAPI) DeleteGateway(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	gwID := vars["gwname"]

	// execute the uninstall action of the node
	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "uninstall",
			Actor:   "gateway",
			Service: gwID,
			Force:   true,
		}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "uninstall", bp)
	errmsg := "Error executing blueprint for gateway uninstallation "
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	// Wait for the uninstall job to be finshed before we delete the service
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for gateway uninstallation")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for gateway uninstallation")
		}
		return
	}

	res, err := aysClient.Ays.DeleteServiceByName(gwID, "gateway", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "deleting service") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
