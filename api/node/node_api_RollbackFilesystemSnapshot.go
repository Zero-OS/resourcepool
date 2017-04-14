package node

import (
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// RollbackFilesystemSnapshot is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystems/{filesystemname}/snapshot/{snapshotname}/rollback
// Rollback the filesystem to the state at the moment the snapshot was taken
func (api NodeAPI) RollbackFilesystemSnapshot(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	name := vars["snapshotname"]

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			"action":  "rollback",
			"actor":   "fssnapshot",
			"service": name,
			"force":   true,
		}},
	}

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "snapshot", name, "rollback", blueprint); err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for fssnapshot rollback : %+v", err)
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
