package node

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// GetContainer is the handler for GET /nodes/{nodeid}/containers/{containername}
// Get Container
func (api NodeAPI) GetContainer(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	containername := vars["containername"]
	service, res, err := api.AysAPI.Ays.GetServiceByName(containername, "container", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, "Getting container service") {
		return
	}

	containerItem := struct {
		Nics           []ContainerNIC
		Filesystems    []string
		Flist          string
		HostNetworking bool
		Hostname       string
		ID             int
		Initprocesses  []CoreSystem
		Ports          []string
		Status         EnumContainerStatus
		Zerotier       string
		Storage        string
	}{}

	if err := json.Unmarshal(service.Data, &containerItem); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	respBody := Container{
		Nics:           containerItem.Nics,
		Zerotier:       containerItem.Zerotier,
		Status:         containerItem.Status,
		Ports:          containerItem.Ports,
		Initprocesses:  containerItem.Initprocesses,
		Hostname:       containerItem.Hostname,
		HostNetworking: containerItem.HostNetworking,
		Flist:          containerItem.Flist,
		Filesystems:    containerItem.Filesystems,
		Storage:        containerItem.Storage,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
