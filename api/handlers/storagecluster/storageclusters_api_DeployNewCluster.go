package storagecluster

import (
	"encoding/json"
	"fmt"

	"github.com/zero-os/0-orchestrator/api/ays"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/httperror"
)

// DeployNewCluster is the handler for POST /storageclusters
// Deploy New Cluster
func (api *StorageclustersAPI) DeployNewCluster(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody ClusterCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	exists, err := api.client.IsServiceExists("storage_cluster", reqBody.Label)
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// exists, err := aysClient.ServiceExists("storage_cluster", reqBody.Label, api.AysRepo)
	// if err != nil {
	// 	errmsg := fmt.Sprintf("error getting storage cluster service by name %s ", reqBody.Label)
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	return
	// }
	if exists {
		httperror.WriteError(w, http.StatusConflict, fmt.Errorf("A storage cluster with label %s already exists", reqBody.Label), "")
		return
	}

	if reqBody.Servers%len(reqBody.Nodes) != 0 {
		httperror.WriteError(w, http.StatusBadRequest, fmt.Errorf("Amount of servers is not equally divisible by amount of nodes"), "")
		return
	}

	blueprint := struct {
		Label        string          `yaml:"label" json:"label"`
		NrServer     int             `yaml:"nrServer" json:"nrServer"`
		DiskType     string          `yaml:"diskType" json:"diskType"`
		MetaDiskType string          `yaml:"metadiskType" json:"metadiskType"`
		Nodes        []string        `yaml:"nodes" json:"nodes"`
		ClusterType  EnumClusterType `yaml:"clusterType" json:"clusterType"`
		DataShards   int             `yaml:"dataShards" json:"dataShards"`
		ParityShards int             `yaml:"parityShards" json:"parityShards"`
	}{
		Label:        reqBody.Label,
		NrServer:     reqBody.Servers,
		DiskType:     string(reqBody.DriveType),
		MetaDiskType: string(reqBody.MetaDriveType),
		Nodes:        reqBody.Nodes,
		ClusterType:  reqBody.ClusterType,
		DataShards:   reqBody.DataShards,
		ParityShards: reqBody.ParityShards,
	}

	if string(blueprint.MetaDiskType) == "" {
		blueprint.MetaDiskType = string(EnumClusterCreateDriveTypessd)
	}

	bp := ays.Blueprint{
		fmt.Sprintf("storage_cluster__%s", reqBody.Label): blueprint,
		"actions": ays.ActionBlock{
			Action:  "install",
			Actor:   "storage_cluster",
			Service: reqBody.Label,
		},
	}
	// obj[] = blueprint
	// obj["actions"] = []tools.ActionBlock{{
	// 	Action:  "install",
	// 	Actor:   "storage_cluster",
	// 	Service: reqBody.Label,
	// }}
	{
		bpName := ays.BlueprintName("storage_cluster", reqBody.Label, "install")
		_, err := api.client.CreateExecRun(bpName, bp, true)
		if err != nil {
			if ayserr, ok := err.(*ays.Error); ok {
				ayserr.Handle(w, http.StatusInternalServerError)
			} else {
				httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
			}
			return
		}
	}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "storage_cluster", reqBody.Label, "install", obj)

	// errmsg := fmt.Sprintf("error executing blueprint for storage_cluster %s creation", reqBody.Label)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }

	w.Header().Set("Location", fmt.Sprintf("/storageclusters/%s", reqBody.Label))
	w.WriteHeader(http.StatusCreated)
}
