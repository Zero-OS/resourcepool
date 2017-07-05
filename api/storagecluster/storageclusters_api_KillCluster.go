package storagecluster

import (
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// KillCluster is the handler for DELETE /storageclusters/{label}
// Kill cluster
func (api StorageclustersAPI) KillCluster(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	storageCluster := vars["label"]

	// Prevent deletion of nonempty clusters
	query := map[string]interface{}{
		"consume": fmt.Sprintf("storage_cluster!%s", storageCluster),
	}
	services, res, err := aysClient.Ays.ListServicesByRole("vdisk", api.AysRepo, nil, query)
	if !tools.HandleAYSResponse(err, res, w, "listing vdisks") {
		return
	}

	if len(services) > 0 {
		err := fmt.Errorf("Can't delete storage clusters with attached vdisks")
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// execute the delete action
	blueprint := map[string]interface{}{
		"actions": []tools.ActionBlock{{
			Action:  "delete",
			Actor:   "storage_cluster",
			Service: storageCluster,
		}},
	}

	_, resp, err := aysClient.Ays.GetServiceByName(storageCluster, "storage_cluster", api.AysRepo, nil, nil)

	if err != nil {
		errmsg := fmt.Sprintf("error executing blueprint for Storage cluster %s deletion", storageCluster)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	if resp.StatusCode == http.StatusNotFound {
		tools.WriteError(w, http.StatusNotFound, fmt.Errorf("Storage cluster %s does not exist", storageCluster), "")
		return
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "storage_cluster", storageCluster, "delete", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error executing blueprint for storage_cluster deletion")
		return
	}

	// Wait for the delete job to be finshed before we delete the service
	if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for storage_cluster deletion")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for storage_cluster deletion")
		}
		return
	}

	_, err = aysClient.Ays.DeleteServiceByName(storageCluster, "storage_cluster", api.AysRepo, nil, nil)

	if err != nil {
		errmsg := fmt.Sprintf("Error in deleting storage_cluster %s", storageCluster)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
