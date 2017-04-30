package node

import (
	"net/http"

	"github.com/g8os/grid/api/tools"
)

// ShutdownVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/shutdown
// Gracefully shutdown the VM
func (api NodeAPI) ShutdownVM(w http.ResponseWriter, r *http.Request) {
	tools.ExecuteVMAction(w, r, api.AysRepo, "shutdown")
}
