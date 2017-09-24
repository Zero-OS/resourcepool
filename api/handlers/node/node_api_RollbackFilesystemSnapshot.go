package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"github.com/gorilla/mux"
)

// RollbackFilesystemSnapshot is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}/snapshot/{snapshotname}/rollback
// Rollback the filesystem to the state at the moment the snapshot was taken
func (api *NodeAPI) RollbackFilesystemSnapshot(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	name := vars["snapshotname"]

	// execute the delete action of the snapshot
	blueprint := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "rollback",
			Actor:   "fssnapshot",
			Service: name,
			Force:   true,
		}},
	}

	bpName := ays.BlueprintName("snapshot", name, "rollback")
	if err := api.client.CreateExec(bpName, blueprint); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// _, err := aysClient.ExecuteBlueprint(api.AysRepo, "snapshot", name, "rollback", blueprint)

	// errmsg := "Error executing blueprint for fssnapshot rollback "
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	w.WriteHeader(http.StatusNoContent)
}
