package storagecluster

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"

	log "github.com/Sirupsen/logrus"
)

// DeployNewCluster is the handler for POST /storageclusters
// Deploy New Cluster
func (api StorageclustersAPI) DeployNewCluster(w http.ResponseWriter, r *http.Request) {
	var reqBody ClusterCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	if reqBody.Servers%len(reqBody.Nodes) != 0 {
		tools.WriteError(w, http.StatusBadRequest, fmt.Errorf("Amount of servers is not equally devidable by amount of nodes"))
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

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "storage_cluster", reqBody.Label, "install", obj); err != nil {
		log.Errorf("error executing blueprint for storage_cluster %s creation : %+v", reqBody.Label, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/storageclusters/%s", reqBody.Label))
	w.WriteHeader(http.StatusCreated)
}
