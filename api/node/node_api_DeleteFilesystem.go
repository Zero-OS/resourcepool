package node

import (
	"fmt"
	"net/http"
	"time"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"

	log "github.com/Sirupsen/logrus"
)

// DeleteFilesystem is the handler for DELETE /node/{nodeid}/storagepool/{storagepoolname}/filesystem/{filesystemname}
// Delete filesystem
func (api NodeAPI) DeleteFilesystem(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	name := vars["filesystemname"]

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []map[string]string{{
			"action":  "delete",
			"actor":   "filesystem",
			"service": name,
		}},
	}
	blueprintName := fmt.Sprintf("filesystem__%s_delete_%d", name, time.Now().Unix())

	run, err := tools.ExecuteBlueprint(api.AysRepo, blueprintName, blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for filesystem deletion : %+v", err.Error())
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

	resp, err := api.AysAPI.Ays.DeleteServiceByName(name, "filesystem", api.AysRepo, nil, nil)
	if err != nil {
		log.Errorf("Error deleting filesystem services : %+v", err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if resp.StatusCode != http.StatusNoContent {
		log.Errorf("Error deleting filesystem services : %+v", resp.Status)
		tools.WriteError(w, resp.StatusCode, fmt.Errorf("bad response from AYS: %s", resp.Status))
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
