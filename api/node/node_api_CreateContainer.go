package node

import (
	"encoding/json"
	"fmt"
	"net/http"

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

	container := struct {
		Nics           []ContainerNIC `json:"nics" yaml:"nics"`
		Filesystems    []string       `json:"filesystems" yaml:"filesystems"`
		Flist          string         `json:"flist" yaml:"flist"`
		HostNetworking bool           `json:"hostNetworking" yaml:"hostNetworking"`
		Hostname       string         `json:"hostname" yaml:"hostname"`
		Node           string         `json:"node" yaml:"node"`
		InitProcesses  []CoreSystem   `json:"initProcesses" yaml:"initProcesses"`
		Ports          []string       `json:"ports" yaml:"ports"`
		Storage        string         `json:"storage" yaml:"storage"`
	}{
		Nics:           reqBody.Nics,
		Filesystems:    reqBody.Filesystems,
		Flist:          reqBody.Flist,
		HostNetworking: reqBody.HostNetworking,
		Hostname:       reqBody.Hostname,
		InitProcesses:  reqBody.InitProcesses,
		Node:           nodeID,
		Ports:          reqBody.Ports,
		Storage:        reqBody.Storage,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("container__%s", reqBody.Id)] = container
	obj["actions"] = []tools.ActionBlock{{Action: "install", Service: reqBody.Id, Actor: "container"}}

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "container", reqBody.Id, "install", obj); err != nil {
		log.Errorf("error executing blueprint for container %s creation : %+v", reqBody.Id, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/containers/%s", nodeID, reqBody.Id))
	w.WriteHeader(http.StatusCreated)

}
