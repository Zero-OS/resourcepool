package storagecluster

import (
	"encoding/json"
	"net/http"
	"strconv"
	"strings"
	"sync"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// StorageEngine Struct that is used to map storageEngine service.
type StorageEngine struct {
	HomeDir   string `json:"homeDir" validate:"nonzero"`
	Bind      string `json:"bind" validate:"nonzero"`
	Master    string `json:"master,omitempty"`
	Container string `json:"container" validate:"nonzero"`
}

// func getStorageEngine(aysClient *tools.AYStool, name string, api StorageclustersAPI, w http.ResponseWriter) (StorageServer, []string, error) {
func (api *StorageclustersAPI) getStorageEngine(name string) (*StorageServer, error) {
	var state EnumStorageServerStatus

	storageEngineService, aysErr := api.client.GetService("storage_engine", name, "", []string{})
	if aysErr != nil {
		return nil, aysErr
	}
	// service, res, err := aysClient.Ays.GetServiceByName(name, "storage_engine", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
	// 	return StorageServer{}, []string{""}, err
	// }
	if storageEngineService.State == "error" {
		state = EnumStorageServerStatuserror
	} else {
		state = EnumStorageServerStatusready
	}

	nameInfo := strings.Split(storageEngineService.Name, "_") // parsing string name from cluster<cid>_<data or metadata>_<id>
	id, err := strconv.Atoi(nameInfo[len(nameInfo)-1])

	storageEngine := &StorageEngine{} // since the storage server type is different from the service schema cannot map it to service so need to create custom struct
	if err := json.Unmarshal(storageEngineService.Data, storageEngine); err != nil {
		return nil, err
	}

	bind := strings.Split(storageEngine.Bind, ":")
	port, err := strconv.Atoi(bind[1])
	if err != nil {
		return nil, err
	}

	storageServer := &StorageServer{
		Container: storageEngine.Container,
		ID:        id,
		IP:        bind[0],
		Port:      port,
		Status:    state,
		Type:      nameInfo[len(nameInfo)-2],
	}
	return storageServer, nil
}

const clusterInfoCacheKey = "clusterInfoCacheKey"

// GetClusterInfo is the handler for GET /storageclusters/{label}
// Get full Information about specific cluster
func (api *StorageclustersAPI) GetClusterInfo(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var (
		vars  = mux.Vars(r)
		label = vars["label"]
	)

	//getting cluster service
	clusterService, err := api.client.GetService("storage_cluster", label, "", []string{})
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// service, res, err := aysClient.Ays.GetServiceByName(label, "storage_cluster", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
	// 	return
	// }
	clusterItem := struct {
		Label          string               `json:"label" validate:"nonzero"`
		Status         EnumClusterStatus    `json:"status" validate:"nonzero"`
		NrServer       uint32               `json:"nrServer" validate:"nonzero"`
		HasSlave       bool                 `json:"hasSlave" validate:"nonzero"`
		DiskType       EnumClusterDriveType `json:"diskType" validate:"nonzero"`
		Filesystems    []string             `json:"filesystems" validate:"nonzero"`
		StorageEngines []string             `json:"storageEngines" validate:"nonzero"`
		Nodes          []string             `json:"nodes" validate:"nonzero"`
	}{}

	if err := json.Unmarshal(clusterService.Data, &clusterItem); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "error unmarshaling ays response")
		return
	}

	storageEngines := make([]*StorageServer, len(clusterItem.StorageEngines))
	errs := make([]error, len(clusterItem.StorageEngines))
	var wg sync.WaitGroup
	//looping over all storageEngine disks relating to this cluster
	wg.Add(len(clusterItem.StorageEngines))
	for i, storageEngineName := range clusterItem.StorageEngines {
		go func(i int, name string) {
			defer wg.Done()
			//getting all storageEngine disk services relating to this cluster to get more info on each storageEngine
			storageServer, err := api.getStorageEngine(name)
			if err != nil {
				errs[i] = err
				return
				// if ayserr, ok := err.(*ays.Error); ok {
				// 	ayserr.Handle(w, http.StatusInternalServerError)
				// } else {
				// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting storageEngine service")
				// }
				// return
			}

			storageEngines[i] = storageServer
			//check wether is data or metadata
			// variant := nameInfo[len(nameInfo)-2]
			// if variant == "data" {
			// 	data = append(data, storageServer)
			// } else if variant == "metadata" {
			// 	metadata = append(metadata, storageServer)
			// }
		}(i, storageEngineName)

	}

	wg.Wait()

	// TODO: better erro handler
	// could create a better error message with all erros that happened
	for _, err := range errs {
		if err != nil {
			if ayserr, ok := err.(*ays.Error); ok {
				ayserr.Handle(w, http.StatusInternalServerError)
			} else {
				httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting storageEngine service")
			}
			return
		}
	}

	var (
		data     = []*StorageServer{}
		metadata = []*StorageServer{}
	)
	for _, engine := range storageEngines {
		if engine.Type == "data" {
			data = append(data, engine)
		} else {
			metadata = append(metadata, engine)
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

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
