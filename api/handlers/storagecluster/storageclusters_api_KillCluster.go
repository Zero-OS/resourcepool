package storagecluster

import (
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// KillCluster is the handler for DELETE /storageclusters/{label}
// Kill cluster
func (api *StorageclustersAPI) KillCluster(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	storageCluster := vars["label"]

	// Prevent deletion of nonempty clusters
	vdiskServices, err := api.client.ListServices("vdisk", ays.ListServiceOpt{
		Consume: fmt.Sprintf("storage_cluster!%s", storageCluster),
	})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// query := map[string]interface{}{
	// 	"consume": fmt.Sprintf("storage_cluster!%s", storageCluster),
	// }
	// services, res, err := aysClient.Ays.ListServicesByRole("vdisk", api.AysRepo, nil, query)
	// if !tools.HandleAYSResponse(err, res, w, "listing vdisks") {
	// 	return
	// }

	if len(vdiskServices) > 0 {
		err := fmt.Errorf("Can't delete storage clusters with attached vdisks")
		httperror.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}

	// execute the delete action
	blueprint := ays.Blueprint{
		"actions": []ays.ActionBlock{{
			Action:  "delete",
			Actor:   "storage_cluster",
			Service: storageCluster,
		}},
	}

	exist, err := api.client.IsServiceExists("storage_cluster", storageCluster)
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// _, resp, err := aysClient.Ays.GetServiceByName(storageCluster, "storage_cluster", api.AysRepo, nil, nil)

	// if err != nil {
	// 	errmsg := fmt.Sprintf("error executing blueprint for Storage cluster %s deletion", storageCluster)
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	return
	// }

	if !exist {
		httperror.WriteError(w, http.StatusNotFound, fmt.Errorf("Storage cluster %s does not exist", storageCluster), "")
		return
	}

	{
		bpName := ays.BlueprintName("storage_cluster", storageCluster, "delete")
		_, err := api.client.CreateExecRun(bpName, blueprint, true)
		if err != nil {
			if ayserr, ok := err.(*ays.Error); ok {
				ayserr.Handle(w, http.StatusInternalServerError)
			} else {
				httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
			}
			return
		}
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "storage_cluster", storageCluster, "delete", blueprint)
	// if err != nil {
	// 	httpErr := err.(httperror.HTTPError)
	// 	httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error executing blueprint for storage_cluster deletion")
	// 	return
	// }

	// // Wait for the delete job to be finshed before we delete the service
	// if _, err = aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	httpErr, ok := err.(httperror.HTTPError)
	// 	if ok {
	// 		httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "Error running blueprint for storage_cluster deletion")
	// 	} else {
	// 		httperror.WriteError(w, http.StatusInternalServerError, err, "Error running blueprint for storage_cluster deletion")
	// 	}
	// 	return
	// }
	if err := api.client.DeleteService("storage_cluster", storageCluster); err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// _, err = aysClient.Ays.DeleteServiceByName(storageCluster, "storage_cluster", api.AysRepo, nil, nil)

	// if err != nil {
	// 	errmsg := fmt.Sprintf("Error in deleting storage_cluster %s", storageCluster)
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	return
	// }
	w.WriteHeader(http.StatusNoContent)
}
