package node

import (
	"encoding/json"
	"fmt"

	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetVM is the handler for GET /nodes/{nodeid}/vms/{vmid}
// Get detailed virtual machine object
func (api *NodeAPI) GetVM(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	vmID := vars["vmid"]

	srv, res, err := aysClient.Ays.GetServiceByName(vmID, "vm", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, fmt.Sprintf("getting vm %s details", vmID)) {
		return
	}

	if srv.Parent.Name != vars["nodeid"] {
		err := fmt.Errorf("vm %s does not exists under %s parent", vars["vmid"], vars["nodeid"])
		tools.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	var vm VM
	if err := json.Unmarshal(srv.Data, &vm); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
		return
	}
	vm.Id = srv.Name

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&vm)
}
