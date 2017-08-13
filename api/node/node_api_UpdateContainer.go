package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// UpdateContainer is the handler for PUT /nodes/{nodeid}/containers/{containername}
// Update a new Container
func (api NodeAPI) UpdateContainer(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody ContainerUpdate

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
	containerName := vars["containername"]

	// validate container name
	exists, err := aysClient.ServiceExists("container", containerName, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking container service exists")
		return
	} else if !exists {
		err = fmt.Errorf("Container with name %s does not exists", containerName)
		tools.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	for _, nic := range reqBody.Nics {
		if err = nic.ValidateServices(aysClient, api.AysRepo); err != nil {
			tools.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("container__%s", containerName)] = reqBody

	if _, err := aysClient.UpdateBlueprint(api.AysRepo, "container", containerName, "install", obj); err != nil {
		errmsg := fmt.Sprintf("error executing blueprint for container %s creation", containerName)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/containers/%s", nodeID, containerName))
	w.WriteHeader(http.StatusCreated)

}
