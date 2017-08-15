package storagecluster

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeployNewCluster is the handler for POST /storageclusters
// Deploy New Cluster
func (api StorageclustersAPI) DeployNewCluster(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody ClusterCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	exists, err := aysClient.ServiceExists("storage_cluster", reqBody.Label, api.AysRepo)
	if err != nil {
		errmsg := fmt.Sprintf("error getting storage cluster service by name %s ", reqBody.Label)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	if exists {
		tools.WriteError(w, http.StatusConflict, fmt.Errorf("A storage cluster with label %s already exists", reqBody.Label), "")
		return
	}

	if reqBody.Servers%len(reqBody.Nodes) != 0 {
		tools.WriteError(w, http.StatusBadRequest, fmt.Errorf("Amount of servers is not equally divisible by amount of nodes"), "")
		return
	}

	blueprint := struct {
		Label       string          `yaml:"label" json:"label"`
		NrServer    int             `yaml:"nrServer" json:"nrServer"`
		DiskType    string          `yaml:"diskType" json:"diskType"`
		Nodes       []string        `yaml:"nodes" json:"nodes"`
		ClusterType EnumClusterType `yaml:"clusterType" json:"clusterType"`
		K           int             `yaml:"k" json:"k"`
		M           int             `yaml:"m" json:"m"`
	}{
		Label:       reqBody.Label,
		NrServer:    reqBody.Servers,
		DiskType:    string(reqBody.DriveType),
		Nodes:       reqBody.Nodes,
		ClusterType: reqBody.ClusterType,
		K:           reqBody.K,
		M:           reqBody.M,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("storage_cluster__%s", reqBody.Label)] = blueprint
	obj["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "storage_cluster",
		Service: reqBody.Label,
	}}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "storage_cluster", reqBody.Label, "install", obj)

	errmsg := fmt.Sprintf("error executing blueprint for storage_cluster %s creation", reqBody.Label)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/storageclusters/%s", reqBody.Label))
	w.WriteHeader(http.StatusCreated)
}
