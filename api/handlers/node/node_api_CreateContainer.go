package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// CreateContainer is the handler for POST /nodes/{nodeid}/containers
// Create a new Container
func (api *NodeAPI) CreateContainer(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody CreateContainer

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	// validate container name
	// exists, err := aysClient.ServiceExists("container", reqBody.Name, api.AysRepo)
	// if err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error checking container service exists")
	// 	return
	// } else if exists {
	// 	err = fmt.Errorf("Container with name %s already exists", reqBody.Name)
	// 	httperror.WriteError(w, http.StatusConflict, err, "")
	// 	return
	// }

	// validate container name
	if exists, err := api.client.IsServiceExists("container", reqBody.Name); exists || err != nil {
		handlers.HandleErrorServiceExists(w, err, "container", reqBody.Name)
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

		// exists, err := aysClient.ServiceExists("storagepool", storagepoolname, api.AysRepo)
		// if err != nil {
		// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error checking storagepool service exists")
		// 	return
		// } else if !exists {
		// 	err = fmt.Errorf("Storagepool with name %s does not exists", storagepoolname)
		// 	httperror.WriteError(w, http.StatusBadRequest, err, "")
		// 	return
		// }
		if exists, err := api.client.IsServiceExists("storagepool", storagepoolname); !exists || err != nil {
			handlers.HandleErrorServiceDoesNotExist(w, err, "storagepool", storagepoolname)
			return
		}
		// exists, err = aysClient.ServiceExists("filesystem", filesystemname, api.AysRepo)
		// if err != nil {
		// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error checking filesystem service exists")
		// 	return
		// } else if !exists {
		// 	err = fmt.Errorf("Filesystem with name %s does not exists", storagepoolname)
		// 	httperror.WriteError(w, http.StatusBadRequest, err, "")
		// 	return
		// }
		if exists, err := api.client.IsServiceExists("filesystem", filesystemname); !exists || err != nil {
			handlers.HandleErrorServiceDoesNotExist(w, err, "filesystem", filesystemname)
			return
		}
		mounts[idx] = mount{Filesystem: parts[1], Target: fmt.Sprintf("/fs/%s/%s", storagepoolname, filesystemname)}
	}

	for _, nic := range reqBody.Nics {
		if err := nic.ValidateServices(api.client); err != nil {
			httperror.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
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

	// obj := make(map[string]interface{})
	// obj[fmt.Sprintf("container__%s", reqBody.Name)] = container
	// obj["actions"] = []tools.ActionBlock{{Action: "install", Service: reqBody.Name, Actor: "container"}}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "container", reqBody.Name, "install", obj)
	// errmsg := fmt.Sprintf("error executing blueprint for container %s creation", reqBody.Name)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }

	serviceName := fmt.Sprintf("container__%s", reqBody.Name)
	blueprint := ays.Blueprint{
		serviceName: container,
		"actions": []ays.ActionBlock{{
			Action:  "install",
			Actor:   "container",
			Service: reqBody.Name,
		}},
	}
	blueprintName := ays.BlueprintName("container", reqBody.Name, "create")
	if _, err := api.client.CreateExecRun(blueprintName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/containers/%s", nodeID, reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
