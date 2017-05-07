package node

import (
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// DeleteContainer is the handler for DELETE /nodes/{nodeid}/containers/{containername}
// Delete Container instance
func (api NodeAPI) DeleteContainer(w http.ResponseWriter, r *http.Request) {
	tools.DeleteContainerId(r, api)

	vars := mux.Vars(r)
	containername := vars["containername"]

	// execute the delete action of the snapshot
	bp := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "stop",
			Actor:   "container",
			Service: containername,
			Force:   true,
		}},
	}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "container", containername, "stop", bp)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for container deletion : %+v", err.Error())
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

	res, err := api.AysAPI.Ays.DeleteServiceByName(containername, "container", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "deleting service") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
