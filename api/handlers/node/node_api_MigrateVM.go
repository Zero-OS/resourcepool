package node

import (
	"encoding/json"
	"fmt"

	"github.com/zero-os/0-orchestrator/api/ays"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// MigrateVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/migrate
// Migrate the VM to another host
func (api *NodeAPI) MigrateVM(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody VMMigrate
	var vmData VMCreate

	vmID := mux.Vars(r)["vmid"]

	// check if vm has bridge
	service, err := api.client.GetService("vm", vmID, "", nil)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	// service, res, err := aysClient.Ays.GetServiceByName(vmID, "vm", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "listing vms") {
	// 	return
	// }

	if err := json.Unmarshal(service.Data, &vmData); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	for _, nic := range vmData.Nics {
		if nic.Type == EnumNicLinkTypebridge {
			err := fmt.Errorf("live migration is not supported for vms with bridges")
			httperror.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
	}

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// Create migrate blueprint
	bp := struct {
		Node string `yaml:"node" json:"node"`
	}{
		Node: reqBody.Nodeid,
	}

	exists, err := api.client.IsServiceExists("node", reqBody.Nodeid)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	if !exists {
		errmsg := fmt.Errorf("node %s does not exist", reqBody.Nodeid)
		httperror.WriteError(w, http.StatusBadRequest, errmsg, "")
		return
	}

	obj := ays.Blueprint{
		fmt.Sprintf("vm__%v", vmID): bp,
	}

	// And execute
	bpName := ays.BlueprintName("vm", vmID, "migrate")
	if _, err := api.client.CreateExecRun(bpName, obj); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vm", vmID, "migrate", obj)

	// errmsg := fmt.Sprintf("error executing blueprint for vm %s migration", vmID)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }
	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/vms/%s", reqBody.Nodeid, vmID))
	w.WriteHeader(http.StatusNoContent)

}
