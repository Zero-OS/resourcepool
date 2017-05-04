package node

import (
	"net/http"

	"github.com/g8os/grid/api/tools"
)

// PauseVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/pause
// Pauses the VM
func (api NodeAPI) PauseVM(w http.ResponseWriter, r *http.Request) {
	tools.ExecuteVMAction(w, r, api.AysRepo, "pause")
}
