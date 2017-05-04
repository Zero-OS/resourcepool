package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	log "github.com/Sirupsen/logrus"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// CreateContainer is the handler for POST /nodes/{nodeid}/containers
// Create a new Container
func (api NodeAPI) CreateContainer(w http.ResponseWriter, r *http.Request) {
	var reqBody CreateContainer

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

	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	_, res, err := api.AysAPI.Ays.GetServiceByName(reqBody.Name, "container", api.AysRepo, nil, nil)

	if err != nil {
		log.Errorf("AYS threw error while %+v.\n", err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	} else if res.StatusCode == http.StatusOK {
		err = fmt.Errorf("Container with name %s already exists", reqBody.Name)
		tools.WriteError(w, http.StatusConflict, err)
		return
	}
	if res.StatusCode != http.StatusNotFound {
		err = fmt.Errorf("AYS returned status %d while getting service", res.StatusCode)
		tools.WriteError(w, res.StatusCode, err)
		return
	}

	type mount struct {
		Filesystem string `json:"filesystem" yaml:"filesystem"`
		Target     string `json:"target" yaml:"target"`
	}

	var mounts = make([]mount, len(reqBody.Filesystems))
	for idx, filesystem := range reqBody.Filesystems {
		parts := strings.Split(filesystem, ":")
		mounts[idx] = mount{Filesystem: parts[1], Target: fmt.Sprintf("/fs/%s/%s", parts[0], parts[1])}
	}

	container := struct {
		Nics           []ContainerNIC `json:"nics" yaml:"nics"`
		Mounts         []mount        `json:"mounts" yaml:"mounts"`
		Flist          string         `json:"flist" yaml:"flist"`
		HostNetworking bool           `json:"hostNetworking" yaml:"hostNetworking"`
		Hostname       string         `json:"hostname" yaml:"hostname"`
		Node           string         `json:"node" yaml:"node"`
		InitProcesses  []CoreSystem   `json:"initProcesses" yaml:"initProcesses"`
		Ports          []string       `json:"ports" yaml:"ports"`
		Storage        string         `json:"storage" yaml:"storage"`
	}{
		Nics:           reqBody.Nics,
		Mounts:         mounts,
		Flist:          reqBody.Flist,
		HostNetworking: reqBody.HostNetworking,
		Hostname:       reqBody.Hostname,
		InitProcesses:  reqBody.InitProcesses,
		Node:           nodeID,
		Ports:          reqBody.Ports,
		Storage:        reqBody.Storage,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("container__%s", reqBody.Name)] = container
	obj["actions"] = []tools.ActionBlock{{Action: "install", Service: reqBody.Name, Actor: "container"}}

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "container", reqBody.Name, "install", obj); err != nil {
		log.Errorf("error executing blueprint for container %s creation : %+v", reqBody.Name, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/containers/%s", nodeID, reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
