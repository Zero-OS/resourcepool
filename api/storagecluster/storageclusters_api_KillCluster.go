package storagecluster

import (
	"fmt"
	"net/http"

	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"

	log "github.com/Sirupsen/logrus"
)

// KillCluster is the handler for DELETE /storageclusters/{label}
// Kill cluster
func (api StorageclustersAPI) KillCluster(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	storageCluster := vars["label"]

	// execute the delete action
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "delete",
			Actor:   "storage_cluster",
			Service: storageCluster,
		}},
	}

	_, resp, err := api.AysAPI.Ays.GetServiceByName(storageCluster, "storage_cluster", api.AysRepo, nil, nil)

	if err != nil {
		log.Errorf("error executing blueprint for Storage cluster %s deletion : %+v", storageCluster, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if resp.StatusCode == http.StatusNotFound {
		tools.WriteError(w, http.StatusNotFound, fmt.Errorf("Storage cluster %s does not exist", storageCluster))
		return
	}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "storage_cluster", storageCluster, "delete", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for storage_cluster deletion : %+v", err.Error())
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

	_, err = api.AysAPI.Ays.DeleteServiceByName(storageCluster, "storage_cluster", api.AysRepo, nil, nil)

	if err != nil {
		log.Errorf("Error in deleting storage_cluster %s : %+v", storageCluster, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
