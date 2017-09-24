package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/handlers"
)

// StartVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/start
// Starts the VM
func (api *NodeAPI) StartVM(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	if err := api.client.ExecuteVMAction(r, "start"); err != nil {
		handlers.HandleError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
