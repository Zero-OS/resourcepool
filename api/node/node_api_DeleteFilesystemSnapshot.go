package node

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteFilesystemSnapshot is the handler for DELETE /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}/snapshot/{snapshotname}
// Delete snapshot
func (api NodeAPI) DeleteFilesystemSnapshot(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
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

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "fssnapshot", name, "delete", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := "Error executing blueprint for fssnapshot deletion "
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for fssnapshot deletion")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for fssnapshot deletion")
		}
		return
	}

	resp, err := aysClient.Ays.DeleteServiceByName(name, "fssnapshot", api.AysRepo, nil, nil)
	if err != nil {
		errmsg := "Error deleting fssnapshot services "
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	if resp.StatusCode != http.StatusNoContent {
		errmsg := fmt.Sprintf("Error deleting fssnapshot services : %+v", resp.Status)
		tools.WriteError(w, resp.StatusCode, fmt.Errorf("bad response from AYS: %s", resp.Status), errmsg)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
