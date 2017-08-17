package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// UpdateContainer is the handler for PUT /nodes/{nodeid}/containers/{containername}
// Update a new Container
func (api NodeAPI) UpdateContainer(w http.ResponseWriter, r *http.Request) {
	var reqBody ContainerUpdate
	aysClient := tools.GetAysConnection(r, api)
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

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

	// check that ovs exists for vlans and vxlans
	container := client.Container(cl)
	tags := []string{"ovs"}
	containers, err := container.Find(tags)
	ovs := len(containers) == 0

	for _, nic := range reqBody.Nics {
		if err = nic.ValidateServices(aysClient, api.AysRepo); err != nil {
			tools.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
		if nic.Type == EnumContainerNICTypevlan || nic.Type == EnumContainerNICTypevxlan {
			if err != nil {
				err = fmt.Errorf("Error searching container Tags", containerName)
				tools.WriteError(w, http.StatusInternalServerError, err, "")
				return
			} else if ovs {
				err = fmt.Errorf("OVS container needed to run this blueprint", containerName)
				tools.WriteError(w, http.StatusForbidden, err, "") // should have beem forbidden but for consistency bad request
				return
			}
		}
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("container__%s", containerName)] = reqBody

	if _, err := aysClient.UpdateBlueprint(api.AysRepo, "container", containerName, "install", obj); err != nil {
		errmsg := fmt.Sprintf("error executing blueprint for container %s update", containerName)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/containers/%s", nodeID, containerName))
	w.WriteHeader(http.StatusCreated)

}
