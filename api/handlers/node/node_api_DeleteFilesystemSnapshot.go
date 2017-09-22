package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
)

// DeleteFilesystemSnapshot is the handler for DELETE /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}/snapshot/{snapshotname}
// Delete snapshot
func (api *NodeAPI) DeleteFilesystemSnapshot(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	name := vars["snapshotname"]

	// execute the delete action of the snapshot
	blueprint := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "delete",
			Actor:   "fssnapshot",
			Service: name,
			Force:   true,
		}},
	}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "fssnapshot", name, "delete", blueprint)
	// errmsg := "Error executing blueprint for fssnapshot deletion "
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// // Wait for the delete job to be finshed before we delete the service
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for fssnapshot deletion")
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for fssnapshot deletion")
	// 	}
	// 	return
	// }
	blueprintName := ays.BlueprintName("fssnapshot", name, "delete")
	if _, err := api.client.CreateExecRun(blueprintName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}

	// resp, err := aysClient.Ays.DeleteServiceByName(name, "fssnapshot", api.AysRepo, nil, nil)
	// if err != nil {
	// 	errmsg := "Error deleting fssnapshot services "
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	return
	// }

	// if resp.StatusCode != http.StatusNoContent {
	// 	errmsg := fmt.Sprintf("Error deleting fssnapshot services : %+v", resp.Status)
	// 	httperror.WriteError(w, resp.StatusCode, fmt.Errorf("bad response from AYS: %s", resp.Status), errmsg)
	// 	return
	// }

	if err := api.client.DeleteService("fssnapshot", name); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
