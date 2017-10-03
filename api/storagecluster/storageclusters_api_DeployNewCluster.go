package storagecluster

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeployNewCluster is the handler for POST /storageclusters
// Deploy New Cluster
func (api *StorageclustersAPI) DeployNewCluster(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}

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

	role := ""
	if reqBody.ClusterType == EnumClusterTypeBlock {
		role = "block_cluster"
	} else {
		role = "object_cluster"
	}

	exists, err := aysClient.ServiceExists(role, reqBody.Label, api.AysRepo)
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

	// Deploy object cluster
	var obj map[string]interface{}
	if reqBody.ClusterType == EnumClusterTypeBlock {
		obj = deployBlockCluster(aysClient, reqBody)
	} else {
		obj = deployObjectCluster(aysClient, reqBody)
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "block_cluster", reqBody.Label, "install", obj)

	errmsg := fmt.Sprintf("error executing blueprint for storage cluster %s creation", reqBody.Label)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}
	w.Header().Set("Location", fmt.Sprintf("/storageclusters/%s", reqBody.Label))
	w.WriteHeader(http.StatusCreated)
}

func deployObjectCluster(aysClient *tools.AYStool, reqBody ClusterCreate) map[string]interface{} {
	blueprint := struct {
		Label                string   `yaml:"label" json:"label"`
		NrServer             int      `yaml:"nrServer" json:"nrServer"`
		DataDiskType         string   `yaml:"dataDiskType" json:"dataDiskType"`
		MetaDiskType         string   `yaml:"metaDiskType" json:"metaDiskType"`
		Nodes                []string `yaml:"nodes" json:"nodes"`
		DataShards           int      `yaml:"dataShards" json:"dataShards"`
		ParityShards         int      `yaml:"parityShards" json:"parityShards"`
		ServersPerMetaDrive  int      `yaml:"serversPerMetaDrive" json:"serversPerMetaDrive"`
		ZerostorOrganization string   `yaml:"zerostorOrganization" json:"zerostorOrganization"`
		ZerostorNamespace    string   `yaml:"zerostorNamespace" json:"zerostorNamespace"`
		ZerostorClientID     string   `yaml:"zerostorClientID" json:"zerostorClientID"`
		ZerostorSecret       string   `yaml:"zerostorSecret" json:"zerostorSecret"`
	}{
		Label:                reqBody.Label,
		NrServer:             reqBody.Servers,
		DataDiskType:         string(reqBody.DriveType),
		MetaDiskType:         string(reqBody.MetaDriveType),
		Nodes:                reqBody.Nodes,
		DataShards:           reqBody.DataShards,
		ParityShards:         reqBody.ParityShards,
		ServersPerMetaDrive:  reqBody.ServersPerMetaDrive,
		ZerostorOrganization: reqBody.ZerostorOrganization,
		ZerostorNamespace:    reqBody.ZerostorNamespace,
		ZerostorClientID:     reqBody.ZerostorClientID,
		ZerostorSecret:       reqBody.ZerostorSecret,
	}

	if string(blueprint.MetaDiskType) == "" {
		blueprint.MetaDiskType = string(EnumClusterCreateDriveTypessd)
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("object_cluster__%s", reqBody.Label)] = blueprint
	obj["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "object_cluster",
		Service: reqBody.Label,
	}}
	return obj
}

func deployBlockCluster(aysClient *tools.AYStool, reqBody ClusterCreate) map[string]interface{} {
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
	obj[fmt.Sprintf("block_cluster__%s", reqBody.Label)] = blueprint
	obj["actions"] = []tools.ActionBlock{{
		Action:  "install",
		Actor:   "block_cluster",
		Service: reqBody.Label,
	}}
	return obj
}
