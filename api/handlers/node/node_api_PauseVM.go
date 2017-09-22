package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/handlers"
)

// PauseVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/pause
// Pauses the VM
func (api *NodeAPI) PauseVM(w http.ResponseWriter, r *http.Request) {
	if err := api.client.ExecuteVMAction(r, "pause"); err != nil {
		handlers.HandleError(w, err)
	}
	w.WriteHeader(http.StatusNoContent)
}
