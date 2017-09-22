package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/handlers"
)

// ShutdownVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/shutdown
// Gracefully shutdown the VM
func (api *NodeAPI) ShutdownVM(w http.ResponseWriter, r *http.Request) {
	if err := api.client.ExecuteVMAction(r, "shutdown"); err != nil {
		handlers.HandlesError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
