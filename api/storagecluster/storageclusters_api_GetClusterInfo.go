package storagecluster

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"strings"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
	cache "github.com/pmylund/go-cache"
)

// Ardb Struct that is used to map ardb service.
type Ardb struct {
	HomeDir   string `json:"homeDir" validate:"nonzero"`
	Bind      string `json:"bind" validate:"nonzero"`
	Master    string `json:"master,omitempty"`
	Container string `json:"container" validate:"nonzero"`
}

func getArdb(name string, api StorageclustersAPI, w http.ResponseWriter) (StorageServer, Ardb, []string, error) {
	var state EnumStorageServerStatus
	service, res, err := api.AysAPI.Ays.GetServiceByName(name, "ardb", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
		return StorageServer{}, Ardb{}, []string{""}, err
	}
	if service.State == "error" {
		state = EnumStorageServerStatuserror
	} else {
		state = EnumStorageServerStatusready
	}

	nameInfo := strings.Split(service.Name, "_") // parsing string name from cluster<cid>_<data or metadata>_<id>
	id, err := strconv.Atoi(nameInfo[2])
	ardb := Ardb{} // since the storage server type is different from the service schema cannot map it to service so need to create custom struct
	if err := json.Unmarshal(service.Data, &ardb); err != nil {
		return StorageServer{}, Ardb{}, []string{""}, err
	}
	bind := strings.Split(ardb.Bind, ":")
	port, err := strconv.Atoi(bind[1])
	if err != nil {
		return StorageServer{}, Ardb{}, []string{""}, err
	}
	storageServer := StorageServer{
		Container: ardb.Container,
		ID:        id,
		IP:        bind[0],
		Port:      port,
		Status:    state,
	}
	return storageServer, ardb, nameInfo, nil
}

const clusterInfoCacheKey = "clusterInfoCacheKey"

// GetClusterInfo is the handler for GET /storageclusters/{label}
// Get full Information about specific cluster
func (api StorageclustersAPI) GetClusterInfo(w http.ResponseWriter, r *http.Request) {
	var metadata []HAStorageServer
	var data []HAStorageServer
	vars := mux.Vars(r)
	label := vars["label"]

	cacheKey := fmt.Sprintf("%s:%s", clusterInfoCacheKey, label)
	if info, found := api.cache.Get(cacheKey); found {
		log.Debugf("get %s cluster info from cache", label)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(info.([]byte))
		return
	}

	//getting cluster service
	service, res, err := api.AysAPI.Ays.GetServiceByName(label, "storage_cluster", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
		return
	}
	clusterItem := struct {
		Label       string               `json:"label" validate:"nonzero"`
		Status      EnumClusterStatus    `json:"status" validate:"nonzero"`
		NrServer    uint32               `json:"nrServer" validate:"nonzero"`
		HasSlave    bool                 `json:"hasSlave" validate:"nonzero"`
		DiskType    EnumClusterDriveType `json:"diskType" validate:"nonzero"`
		Filesystems []string             `json:"filesystems" validate:"nonzero"`
		Ardbs       []string             `json:"ardbs" validate:"nonzero"`
		Nodes       []string             `json:"nodes" validate:"nonzero"`
	}{}

	if err := json.Unmarshal(service.Data, &clusterItem); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	//looping over all ardb disks relating to this cluster
	for _, ardbName := range clusterItem.Ardbs {
		//getting all ardb disk services relating to this cluster to get more info on each ardb
		storageServer, ardb, nameInfo, err := getArdb(ardbName, api, w)
		relation := HAStorageServer{}
		if err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err)
			return
		}
		//set relation as master or slave
		if ardb.Master == "" {
			relation.Master = &storageServer
			relation.Slave = nil
		} else {
			relation.Slave = &storageServer

			master, _, _, err := getArdb(ardb.Master, api, w)
			if err != nil {
				tools.WriteError(w, http.StatusInternalServerError, err)
				return
			}
			relation.Master = &master
		}

		//check wether is data or metadata
		if nameInfo[1] == "data" {
			data = append(data, relation)
		} else if nameInfo[1] == "metadata" {
			metadata = append(metadata, relation)
		}

	}

	respBody := Cluster{
		Label:           clusterItem.Label,
		Status:          clusterItem.Status,
		DriveType:       clusterItem.DiskType,
		Nodes:           clusterItem.Nodes,
		MetadataStorage: metadata,
		DataStorage:     data,
	}

	buff := &bytes.Buffer{}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(buff).Encode(&respBody)

	info := buff.Bytes()
	api.cache.Set(cacheKey, info, cache.DefaultExpiration)
	w.Write(info)
}
