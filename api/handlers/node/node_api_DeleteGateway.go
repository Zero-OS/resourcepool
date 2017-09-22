package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
)

// DeleteGateway is the handler for DELETE /nodes/{nodeid}/gws/{gwname}
// Delete gateway instance
func (api *NodeAPI) DeleteGateway(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	gwID := vars["gwname"]

	// execute the uninstall action of the node
	bp := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "uninstall",
			Actor:   "gateway",
			Service: gwID,
			Force:   true,
		}},
	}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "uninstall", bp)
	// errmsg := "Error executing blueprint for gateway uninstallation "
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }
	bpName := ays.BlueprintName("gateway", gwID, "uninstall")
	_, err := api.client.CreateExecRun(bpName, obj, true)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	// // Wait for the uninstall job to be finshed before we delete the service
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for gateway uninstallation")
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for gateway uninstallation")
	// 	}
	// 	return
	// }

	// res, err := aysClient.Ays.DeleteServiceByName(gwID, "gateway", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "deleting service") {
	// 	return
	// }
	if err := api.client.DeleteService("gateway", gwID); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
