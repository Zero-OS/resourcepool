package storagecluster

import (
	"encoding/json"
	"net/http"
	"strconv"
	"strings"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// StorageEngine Struct that is used to map storageEngine service.
type StorageEngine struct {
	HomeDir   string `json:"homeDir" validate:"nonzero"`
	Bind      string `json:"bind" validate:"nonzero"`
	Master    string `json:"master,omitempty"`
	Container string `json:"container" validate:"nonzero"`
}

func getStorageEngine(aysClient *tools.AYStool, name string, api *StorageclustersAPI, role string) (StorageServer, []string, error) {
	var state EnumStorageServerStatus
	service, _, err := aysClient.Ays.GetServiceByName(name, role, api.AysRepo, nil, nil)
	if err != nil {
		return StorageServer{}, []string{""}, err
	}
	if service.State == "error" {
		state = EnumStorageServerStatuserror
	} else {
		state = EnumStorageServerStatusready
	}

	nameInfo := strings.Split(service.Name, "_") // parsing string name from cluster<cid>_<data or metadata>_<id>
	id, err := strconv.Atoi(nameInfo[len(nameInfo)-1])
	storageEngine := StorageEngine{} // since the storage server type is different from the service schema cannot map it to service so need to create custom struct
	if err := json.Unmarshal(service.Data, &storageEngine); err != nil {
		return StorageServer{}, []string{""}, err
	}
	bind := strings.Split(storageEngine.Bind, ":")
	port, err := strconv.Atoi(bind[1])
	if err != nil {
		return StorageServer{}, []string{""}, err
	}
	storageServer := StorageServer{
		Container: storageEngine.Container,
		ID:        id,
		IP:        bind[0],
		Port:      port,
		Status:    state,
	}
	return storageServer, nameInfo, nil
}

const clusterInfoCacheKey = "clusterInfoCacheKey"

// GetClusterInfo is the handler for GET /storageclusters/{label}
// Get full Information about specific cluster
func (api *StorageclustersAPI) GetClusterInfo(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	var data []StorageServer
	vars := mux.Vars(r)
	label := vars["label"]

	//getting cluster service
	service, res, err := aysClient.Ays.GetServiceByName(label, "storagecluster", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
		return
	}

	clusterItem := struct {
		Label               string               `json:"label" validate:"nonzero"`
		Status              EnumClusterStatus    `json:"status" validate:"nonzero"`
		NrServer            uint32               `json:"nrServer" validate:"nonzero"`
		DiskType            EnumClusterDriveType `json:"diskType" validate:"nonzero"`
		DataDiskType        EnumClusterDriveType `json:"dataDiskType"`
		MetaDiskType        EnumClusterDriveType `json:"metaDiskType"`
		ServersPerMetaDrive uint32               `json:"serversPerMetaDrive"`
		StorageServers      []string             `json:"storageServers" validate:"nonzero"`
		Nodes               []string             `json:"nodes" validate:"nonzero"`
	}{}

	if err := json.Unmarshal(service.Data, &clusterItem); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "error unmarshaling ays response")
		return
	}

	respBody := Cluster{
		Label:         clusterItem.Label,
		Status:        clusterItem.Status,
		DriveType:     clusterItem.DiskType,
		Nodes:         clusterItem.Nodes,
		MetaDriveType: clusterItem.MetaDiskType,
	}

	if clusterItem.MetaDiskType != "" {
		respBody.ClusterType = EnumClusterTypeObject
	} else {
		respBody.ClusterType = EnumClusterTypeBlock
	}
	//looping over all storageEngine disks relating to this cluster
	serverRole := "storage_engine"
	respBody.DriveType = clusterItem.DiskType

	if clusterItem.ServersPerMetaDrive != 0 {
		serverRole = "zerostor"
		respBody.DriveType = clusterItem.DataDiskType
		respBody.MetaDriveType = clusterItem.MetaDiskType
	}
	for _, storageServerName := range clusterItem.StorageServers {
		//getting all storageEngine disk services relating to this cluster to get more info on each storageEngine
		storageServer, _, err := getStorageEngine(aysClient, storageServerName, api, serverRole)
		if err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error getting storageServer service")
			return
		}
		data = append(data, storageServer)
	}

	respBody.StorageServers = data

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
