package node

import (
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// DeleteFilesystemSnapshot is the handler for DELETE /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}/snapshot/{snapshotname}
// Delete snapshot
func (api NodeAPI) DeleteFilesystemSnapshot(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	name := vars["snapshotname"]

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "delete",
			Actor:   "fssnapshot",
			Service: name,
			Force:   true,
		}},
	}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "fssnapshot", name, "delete", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for fssnapshot deletion : %+v", err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if err = tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err)
		}
		return
	}

	resp, err := api.AysAPI.Ays.DeleteServiceByName(name, "fssnapshot", api.AysRepo, nil, nil)
	if err != nil {
		log.Errorf("Error deleting fssnapshot services : %+v", err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if resp.StatusCode != http.StatusNoContent {
		log.Errorf("Error deleting fssnapshot services : %+v", resp.Status)
		tools.WriteError(w, resp.StatusCode, fmt.Errorf("bad response from AYS: %s", resp.Status))
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
