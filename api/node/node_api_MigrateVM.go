package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// MigrateVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/migrate
// Migrate the VM to another host
func (api *NodeAPI) MigrateVM(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody VMMigrate
	var vmData VMCreate

	vmID := mux.Vars(r)["vmid"]

	// check if vm has bridge
	service, res, err := aysClient.Ays.GetServiceByName(vmID, "vm", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "listing vms") {
		return
	}
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

	_, res, err = aysClient.Ays.GetServiceByName(reqBody.Nodeid, "node", api.AysRepo, nil, nil)
	if res.StatusCode == http.StatusNotFound {
		errmsg := fmt.Errorf("node %s does not exist", reqBody.Nodeid)
		httperror.WriteError(w, http.StatusBadRequest, errmsg, "")
		return
	}
	if !tools.HandleAYSResponse(err, res, w, "listing nodes") {
		return
	}

	decl := fmt.Sprintf("vm__%v", vmID)

	obj := make(map[string]interface{})
	obj[decl] = bp

	// And execute

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vm", vmID, "migrate", obj)

	errmsg := fmt.Sprintf("error executing blueprint for vm %s migration", vmID)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}
	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/vms/%s", reqBody.Nodeid, vmID))
	w.WriteHeader(http.StatusNoContent)

}
