package volume

import (
	"net/http"

	log "github.com/Sirupsen/logrus"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// DeleteVolume is the handler for DELETE /volumes/{volumeid}
// Delete Volume
func (api VolumesAPI) DeleteVolume(w http.ResponseWriter, r *http.Request) {

	vars := mux.Vars(r)
	volumeID := vars["volumeid"]

	// execute the delete action of the snapshot
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			"action":  "delete",
			"actor":   "volume",
			"service": volumeID,
			"force":   true,
		}},
	}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "volume", volumeID, "delete", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for volume deletion : %+v", err.Error())
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

	_, err = api.AysAPI.Ays.DeleteServiceByName(volumeID, "volume", api.AysRepo, nil, nil)

	if err != nil {
		log.Errorf("Error in deleting volume %s : %+v", volumeID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
