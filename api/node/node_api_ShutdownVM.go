package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ShutdownVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/shutdown
// Gracefully shutdown the VM
func (api NodeAPI) ShutdownVM(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	tools.ExecuteVMAction(aysClient, w, r, api.AysRepo, "shutdown")
}
