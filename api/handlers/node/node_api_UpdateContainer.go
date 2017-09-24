package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// UpdateContainer is the handler for PUT /nodes/{nodeid}/containers/{containername}
// Update a new Container
func (api *NodeAPI) UpdateContainer(w http.ResponseWriter, r *http.Request) {
	var reqBody ContainerUpdate
	// aysClient := tools.GetAysConnection(r, api)

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
	containerName := vars["containername"]

	// validate container name
	exists, err := api.client.IsServiceExists("container", containerName)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	// exists, err := aysClient.ServiceExists("container", containerName, api.AysRepo)
	// if err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error checking container service exists")
	// 	return
	// } else
	if !exists {
		err = fmt.Errorf("Container with name %s does not exists", containerName)
		httperror.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	for _, nic := range reqBody.Nics {
		if err = nic.ValidateServices(api.client); err != nil {
			httperror.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
	}

	bp := ays.Blueprint{
		fmt.Sprintf("container__%s", containerName): reqBody,
	}
	bpName := ays.BlueprintName("container", containerName, "install")

	if err := api.client.CreateExec(bpName, bp); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// _, err = aysClient.UpdateBlueprint(api.AysRepo, "container", containerName, "install", obj)
	// if !tools.HandleExecuteBlueprintResponse(err, w, "") {
	// 	return
	// }

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/containers/%s", nodeID, containerName))
	w.WriteHeader(http.StatusCreated)

}
