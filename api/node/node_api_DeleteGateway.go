package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteGateway is the handler for DELETE /nodes/{nodeid}/gws/{gwname}
// Delete gateway instance
func (api NodeAPI) DeleteGateway(w http.ResponseWriter, r *http.Request) {
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

	api.AysAPI.AuthHeader = r.Header.Get("Authorization")
	run, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "uninstall", bp)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := "Error executing blueprint for gateway uninstallation "
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		return
	}

	// Wait for the uninstall job to be finshed before we delete the service
	if err = tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for gateway uninstallation")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for gateway uninstallation")
		}
		return
	}

	res, err := api.AysAPI.Ays.DeleteServiceByName(gwID, "gateway", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "deleting service") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
