package node

import (
	"net/http"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// DeleteBridge is the handler for DELETE /node/{nodeid}/bridge/{bridgeid}
// Remove bridge
func (api *NodeAPI) DeleteBridge(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	bridge := vars["bridgeid"]

	// exists, err := aysClient.ServiceExists("bridge", bridge, api.AysRepo)
	// if err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to check for the bridge")
	// 	return
	// }
	// if !exists {
	// 	err = fmt.Errorf("Bridge %s doesn't exist", bridge)
	// 	httperror.WriteError(w, http.StatusNotFound, err, err.Error())
	// 	return
	// }
	if exists, err := api.client.IsServiceExists("bridge", bridge); !exists || err != nil {
		handlers.HandleErrorServiceDoesNotExist(w, err, "bridge", bridge)
		return
	}

	// execute the delete action of the snapshot
	// blueprint := map[string]interface{}{
	// 	"actions": []tools.ActionBlock{{
	// 		Action:  "delete",
	// 		Actor:   "bridge",
	// 		Service: bridge,
	// 		Force:   true,
	// 	}},
	// }

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "bridge", bridge, "delete", blueprint)
	// errmsg := "Error executing blueprint for bridge deletion "
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// // Wait for the delete job to be finshed before we delete the service
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for bridge deletion")
	// 	}
	// 	return
	// }

	blueprint := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "delete",
			Actor:   "bridge",
			Service: bridge,
			Force:   true,
		}},
	}
	blueprintName := ays.BlueprintName("bridge", bridge, "bridge")
	if _, err := api.client.CreateExecRun(blueprintName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}

	if err := api.client.DeleteService(bridge, "bridge"); err != nil {
		errmsg := fmt.Sprintf("Error in deleting bridge %s ", bridge)
		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
