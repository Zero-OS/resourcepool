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

	if reqBody.Servers%len(reqBody.Nodes) != 0 {
		tools.WriteError(w, http.StatusBadRequest, fmt.Errorf("Amount of servers is not equally divisible by amount of nodes"), "")
		return
	}

	blueprint := struct {
		Label    string   `yaml:"label" json:"label"`
		NrServer int      `yaml:"nrServer" json:"nrServer"`
		DiskType string   `yaml:"diskType" json:"diskType"`
		Nodes    []string `yaml:"nodes" json:"nodes"`
	}{
		Label:    reqBody.Label,
		NrServer: reqBody.Servers,
		DiskType: string(reqBody.DriveType),
		Nodes:    reqBody.Nodes,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("storage_cluster__%s", reqBody.Label)] = blueprint
	obj["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "storage_cluster",
		Service: reqBody.Label,
	}}

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "storage_cluster", reqBody.Label, "install", obj); err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for storage_cluster %s creation", reqBody.Label)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/storageclusters/%s", reqBody.Label))
	w.WriteHeader(http.StatusCreated)
}
