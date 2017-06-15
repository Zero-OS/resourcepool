package node

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// RollbackFilesystemSnapshot is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}/snapshot/{snapshotname}/rollback
// Rollback the filesystem to the state at the moment the snapshot was taken
func (api NodeAPI) RollbackFilesystemSnapshot(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
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

	if _, err := aysClient.ExecuteBlueprint(api.AysRepo, "snapshot", name, "rollback", blueprint); err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := "Error executing blueprint for fssnapshot rollback "
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
