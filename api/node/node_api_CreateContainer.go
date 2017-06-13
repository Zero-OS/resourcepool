package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/gorilla/mux"
	runs "github.com/zero-os/0-orchestrator/api/run"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateContainer is the handler for POST /nodes/{nodeid}/containers
// Create a new Container
func (api NodeAPI) CreateContainer(w http.ResponseWriter, r *http.Request) {
	var reqBody CreateContainer

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	// validate container name
	exists, err := tools.ServiceExists("container", reqBody.Name, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking container service exists")
		return
	} else if exists {
		err = fmt.Errorf("Container with name %s already exists", reqBody.Name)
		tools.WriteError(w, http.StatusConflict, err, "")
		return
	}

	type mount struct {
		Filesystem string `json:"filesystem" yaml:"filesystem"`
		Target     string `json:"target" yaml:"target"`
	}

	var mounts = make([]mount, len(reqBody.Filesystems))
	for idx, filesystem := range reqBody.Filesystems {
		parts := strings.Split(filesystem, ":")
		storagepoolname := parts[0]
		filesystemname := parts[1]

		exists, err := tools.ServiceExists("storagepool", storagepoolname, api.AysRepo)
		if err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error checking storagepool service exists")
			return
		} else if !exists {
			err = fmt.Errorf("Storagepool with name %s does not exists", storagepoolname)
			tools.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
		exists, err = tools.ServiceExists("filesystem", filesystemname, api.AysRepo)
		if err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error checking filesystem service exists")
			return
		} else if !exists {
			err = fmt.Errorf("Filesystem with name %s does not exists", storagepoolname)
			tools.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
		mounts[idx] = mount{Filesystem: parts[1], Target: fmt.Sprintf("/fs/%s/%s", storagepoolname, filesystemname)}
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
	api.AysAPI.AuthHeader = r.Header.Get("Authorization")

	run, err := tools.ExecuteBlueprint(api.AysRepo, "container", reqBody.Name, "install", obj)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for container %s creation", reqBody.Name)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}
	response := runs.Run{Runid: run.Key, State: runs.EnumRunState(run.State)}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/containers/%s", nodeID, reqBody.Name))
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(&response)

}
