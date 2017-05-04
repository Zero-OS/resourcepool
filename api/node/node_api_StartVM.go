package node

import (
	"net/http"

	"github.com/g8os/grid/api/tools"
)

// StartVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/start
// Starts the VM
func (api NodeAPI) StartVM(w http.ResponseWriter, r *http.Request) {
	tools.ExecuteVMAction(w, r, api.AysRepo, "start")
}
