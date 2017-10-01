package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// StartVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/start
// Starts the VM
func (api *NodeAPI) StartVM(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	tools.ExecuteVMAction(aysClient, w, r, api.AysRepo, "start")
}
