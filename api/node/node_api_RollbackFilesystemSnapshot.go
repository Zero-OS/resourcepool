package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// RollbackFilesystemSnapshot is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}/snapshot/{snapshotname}/rollback
// Rollback the filesystem to the state at the moment the snapshot was taken
func (api *NodeAPI) RollbackFilesystemSnapshot(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	name := vars["snapshotname"]

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "rollback",
			Actor:   "fssnapshot",
			Service: name,
			Force:   true,
		}},
	}

	_, err = aysClient.ExecuteBlueprint(api.AysRepo, "snapshot", name, "rollback", blueprint)

	errmsg := "Error executing blueprint for fssnapshot rollback "
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
